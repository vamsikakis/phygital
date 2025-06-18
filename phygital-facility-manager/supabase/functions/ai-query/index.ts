// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

console.log("AI query edge function initiated")

// OpenAI API configuration
const OPENAI_API_KEY = Deno.env.get('OPENAI_API_KEY') ?? ''
const OPENAI_API_ORG = Deno.env.get('OPENAI_API_ORG') ?? ''

const SYSTEM_PROMPT = `
You are an AI assistant for the Gopalan Atlantis residential facility management system.
You have access to information about the facility including documents, announcements, events, 
maintenance tickets, and general information about the property.

When answering queries, follow these guidelines:
1. Be concise and accurate in your responses.
2. When you don't know something, admit it rather than guessing.
3. For facility-specific questions, reference the data provided.
4. Format your responses in a clear, professional manner.
5. Prioritize residents' safety and well-being in your answers.

The Gopalan Atlantis is a residential apartment complex in Bangalore, India with the following amenities:
- Swimming pool
- Gym/fitness center
- Community hall
- Children's play area
- Sports facilities (badminton court, tennis court)
- 24/7 security
- Power backup
- Water treatment plant
- Landscaped gardens
`

// Query types with context building strategies
const QUERY_TYPES = {
  general: {
    description: "General queries about facility management",
    contextBuilder: async (supabase, query) => {
      // For general queries, include recent announcements and events
      const { data: announcements } = await supabase
        .from('announcements')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(3)
      
      const { data: events } = await supabase
        .from('events')
        .select('*')
        .gte('date', new Date().toISOString().split('T')[0])
        .order('date', { ascending: true })
        .limit(3)
      
      let context = "Recent announcements:\n"
      if (announcements && announcements.length > 0) {
        announcements.forEach(a => {
          context += `- ${a.title}: ${a.content.substring(0, 100)}...\n`
        })
      } else {
        context += "No recent announcements.\n"
      }
      
      context += "\nUpcoming events:\n"
      if (events && events.length > 0) {
        events.forEach(e => {
          context += `- ${e.title} on ${e.date} at ${e.location}: ${e.description.substring(0, 100)}...\n`
        })
      } else {
        context += "No upcoming events.\n"
      }
      
      return context
    }
  },
  document: {
    description: "Document search and information",
    contextBuilder: async (supabase, query) => {
      // For document queries, search document titles and descriptions
      const { data: documents } = await supabase
        .from('documents')
        .select('*')
        .or(`title.ilike.%${query}%,description.ilike.%${query}%`)
        .order('created_at', { ascending: false })
        .limit(5)
      
      let context = "Relevant documents:\n"
      if (documents && documents.length > 0) {
        documents.forEach(doc => {
          context += `- ${doc.title}: ${doc.description?.substring(0, 100) || 'No description'}...\n`
          if (doc.summary) {
            context += `  Summary: ${doc.summary.substring(0, 150)}...\n`
          }
        })
      } else {
        context += "No relevant documents found.\n"
      }
      
      return context
    }
  },
  ticket: {
    description: "Maintenance ticket information",
    contextBuilder: async (supabase, query, userId) => {
      // For ticket queries, get user's tickets or general ticket info
      let ticketsQuery = supabase
        .from('tickets')
        .select('*')
        
      // If user ID is provided, filter by their tickets
      if (userId) {
        ticketsQuery = ticketsQuery.eq('created_by', userId)
      }
      
      const { data: tickets } = await ticketsQuery
        .or(`subject.ilike.%${query}%,description.ilike.%${query}%`)
        .order('created_at', { ascending: false })
        .limit(5)
      
      let context = "Relevant maintenance tickets:\n"
      if (tickets && tickets.length > 0) {
        tickets.forEach(ticket => {
          context += `- Ticket #${ticket.id.substring(0, 8)}: ${ticket.subject} (${ticket.status})\n`
          context += `  Description: ${ticket.description.substring(0, 100)}...\n`
        })
      } else {
        context += userId 
          ? "You don't have any relevant maintenance tickets.\n"
          : "No relevant maintenance tickets found.\n"
      }
      
      return context
    }
  },
  amenity: {
    description: "Facility amenity information",
    contextBuilder: async (supabase, query) => {
      // For amenity queries, get amenity information and schedules
      const { data: amenities } = await supabase
        .from('amenities')
        .select('*')
        .or(`name.ilike.%${query}%,description.ilike.%${query}%`)
        .limit(3)
      
      let context = "Amenity information:\n"
      if (amenities && amenities.length > 0) {
        amenities.forEach(amenity => {
          context += `- ${amenity.name}: ${amenity.description}\n`
          context += `  Hours: ${amenity.hours || 'N/A'}\n`
          context += `  Location: ${amenity.location || 'N/A'}\n`
          if (amenity.rules) {
            context += `  Rules: ${amenity.rules}\n`
          }
        })
      } else {
        // Provide default information about common amenities
        context += "Standard amenity information:\n"
        context += "- Swimming pool: Open 6 AM to 9 PM daily. Children must be supervised.\n"
        context += "- Gym: Open 5 AM to 10 PM daily. Proper workout attire required.\n"
        context += "- Community hall: Available for booking through management office.\n"
        context += "- Sports courts: Open 6 AM to 9 PM, booking required through the app.\n"
      }
      
      return context
    }
  }
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { query, query_type = 'general', user_id } = await req.json()
    
    if (!query) {
      return new Response(
        JSON.stringify({ error: 'query is required' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }
    
    // Create Supabase client with Admin privileges
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    // Build context for the AI based on query type
    const queryTypeConfig = QUERY_TYPES[query_type] || QUERY_TYPES.general
    let context = await queryTypeConfig.contextBuilder(supabaseClient, query, user_id)
    
    // Log the query
    await supabaseClient
      .from('ai_query_logs')
      .insert({
        query,
        query_type,
        user_id,
        context: context.substring(0, 1000) // Truncate if too long
      })
    
    // Call OpenAI API
    const response = await callOpenAI(query, context)
    
    // Update the log with the response
    await supabaseClient
      .from('ai_query_logs')
      .update({
        response: response.substring(0, 1000), // Truncate if too long
        tokens_used: response.length / 4 // Rough estimate
      })
      .eq('query', query)
      .eq('user_id', user_id || '')
    
    return new Response(
      JSON.stringify({
        success: true,
        query,
        response,
        query_type
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 200 }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})

// Function to call OpenAI API
async function callOpenAI(query, context) {
  try {
    // Prepare the messages
    const messages = [
      {
        role: "system",
        content: SYSTEM_PROMPT
      },
      {
        role: "system",
        content: `Context information for the query:\n${context}`
      },
      {
        role: "user",
        content: query
      }
    ]
    
    // Call OpenAI API
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
        "OpenAI-Organization": OPENAI_API_ORG
      },
      body: JSON.stringify({
        model: "gpt-4",
        messages: messages,
        temperature: 0.7,
        max_tokens: 500
      })
    })
    
    const data = await response.json()
    
    if (data.error) {
      throw new Error(`OpenAI API error: ${data.error.message}`)
    }
    
    return data.choices[0].message.content
  } catch (error) {
    console.error(`Error calling OpenAI: ${error.message}`)
    return `Sorry, I encountered an error while processing your query: ${error.message}`
  }
}
