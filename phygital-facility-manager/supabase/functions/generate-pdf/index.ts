// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

console.log("PDF generation edge function initiated")

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { source_type, source_id, template, options } = await req.json()
    
    if (!source_type || !source_id) {
      return new Response(
        JSON.stringify({ error: 'source_type and source_id are required' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }
    
    // Create Supabase client with Admin privileges
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    // Fetch source data based on source_type
    let sourceData
    let error
    
    switch (source_type) {
      case 'document':
        const { data: document, error: docError } = await supabaseClient
          .from('documents')
          .select('*')
          .eq('id', source_id)
          .single()
        
        sourceData = document
        error = docError
        break
        
      case 'ticket':
        const { data: ticket, error: ticketError } = await supabaseClient
          .from('tickets')
          .select('*, ticket_comments(*)')
          .eq('id', source_id)
          .single()
        
        sourceData = ticket
        error = ticketError
        break
        
      case 'event':
        const { data: event, error: eventError } = await supabaseClient
          .from('events')
          .select('*')
          .eq('id', source_id)
          .single()
        
        sourceData = event
        error = eventError
        break
        
      case 'announcement':
        const { data: announcement, error: annError } = await supabaseClient
          .from('announcements')
          .select('*')
          .eq('id', source_id)
          .single()
        
        sourceData = announcement
        error = annError
        break
        
      case 'financial_report':
        const { data: report, error: reportError } = await supabaseClient
          .from('financial_reports')
          .select('*')
          .eq('id', source_id)
          .single()
        
        sourceData = report
        error = reportError
        break
        
      default:
        return new Response(
          JSON.stringify({ error: 'Invalid source_type. Supported types: document, ticket, event, announcement, financial_report' }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
        )
    }
    
    if (error || !sourceData) {
      return new Response(
        JSON.stringify({ error: `Source data not found: ${error?.message || 'Unknown error'}` }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 }
      )
    }
    
    // Generate PDF (simulated for now)
    // In a real implementation, you would:
    // 1. Use a PDF generation library like PDF.js or a service like Puppeteer
    // 2. Apply the selected template to the source data
    // 3. Generate the actual PDF content
    
    console.log(`Generating PDF for ${source_type} with ID ${source_id}`)
    
    // Simulate PDF generation delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // In a real implementation, this would be the actual PDF content
    const pdfContent = "SIMULATED_PDF_CONTENT"
    
    // Upload the PDF to storage
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `${source_type}_${source_id}_${timestamp}.pdf`
    const storagePath = `exports/${filename}`
    
    // Log the export operation
    await supabaseClient
      .from('export_logs')
      .insert({
        source_type,
        source_id,
        export_type: 'pdf',
        filename,
        storage_path: storagePath,
        created_by: options?.user_id,
        status: 'completed',
        metadata: { 
          template: template || 'default',
          options: options || {},
          timestamp: new Date().toISOString() 
        }
      })
    
    // In a real implementation, you would upload the actual PDF to storage
    // and return a signed URL for download
    
    // Simulate a download URL
    const downloadUrl = `${Deno.env.get('SUPABASE_URL')}/storage/v1/object/public/exports/${storagePath}`
    
    return new Response(
      JSON.stringify({
        success: true,
        source_type,
        source_id,
        filename,
        download_url: downloadUrl,
        message: 'PDF generated successfully'
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
