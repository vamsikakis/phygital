// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

console.log("Document processing edge function initiated")

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { document_id, action } = await req.json()
    
    if (!document_id) {
      return new Response(
        JSON.stringify({ error: 'document_id is required' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }
    
    // Create Supabase client with Admin privileges
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    // Fetch document details
    const { data: document, error: docError } = await supabaseClient
      .from('documents')
      .select('*')
      .eq('id', document_id)
      .single()
    
    if (docError || !document) {
      return new Response(
        JSON.stringify({ error: 'Document not found', details: docError }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 }
      )
    }
    
    let result
    
    // Process the document based on the requested action
    switch(action) {
      case 'extract_text':
        result = await extractTextFromDocument(supabaseClient, document)
        break
      
      case 'generate_summary':
        result = await generateDocumentSummary(supabaseClient, document)
        break
      
      case 'optimize_pdf':
        result = await optimizePdf(supabaseClient, document)
        break
      
      case 'convert_to_pdf':
        result = await convertToPdf(supabaseClient, document)
        break
        
      default:
        return new Response(
          JSON.stringify({ error: 'Invalid action. Supported actions: extract_text, generate_summary, optimize_pdf, convert_to_pdf' }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
        )
    }
    
    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 200 }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})

// Function to extract text content from a document
async function extractTextFromDocument(supabase, document) {
  try {
    // For this example, we'll just simulate text extraction
    // In a real implementation, you would use appropriate libraries based on document type
    
    console.log(`Extracting text from document: ${document.id}`)
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Log the operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'extract_text',
        status: 'completed',
        metadata: { processed_at: new Date().toISOString() }
      })
    
    return {
      success: true,
      document_id: document.id,
      operation: 'extract_text',
      message: 'Text extraction completed successfully'
    }
  } catch (error) {
    console.error(`Error extracting text: ${error.message}`)
    
    // Log the failed operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'extract_text',
        status: 'failed',
        metadata: { error: error.message }
      })
    
    throw error
  }
}

// Function to generate a summary of the document using AI
async function generateDocumentSummary(supabase, document) {
  try {
    console.log(`Generating summary for document: ${document.id}`)
    
    // In a real implementation, you would:
    // 1. Extract text from the document if not already available
    // 2. Use OpenAI or another AI service to generate a summary
    // 3. Save the summary back to the document record
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const summary = "This is an automatically generated summary of the document."
    
    // Update the document with the summary
    await supabase
      .from('documents')
      .update({ 
        summary: summary,
        last_updated: new Date().toISOString()
      })
      .eq('id', document.id)
    
    // Log the operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'generate_summary',
        status: 'completed',
        metadata: { 
          summary_length: summary.length,
          processed_at: new Date().toISOString() 
        }
      })
    
    return {
      success: true,
      document_id: document.id,
      operation: 'generate_summary',
      summary: summary,
      message: 'Summary generated successfully'
    }
  } catch (error) {
    console.error(`Error generating summary: ${error.message}`)
    
    // Log the failed operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'generate_summary',
        status: 'failed',
        metadata: { error: error.message }
      })
    
    throw error
  }
}

// Function to optimize a PDF document
async function optimizePdf(supabase, document) {
  try {
    console.log(`Optimizing PDF document: ${document.id}`)
    
    // In a real implementation, you would:
    // 1. Download the PDF from storage
    // 2. Use a PDF library to optimize it
    // 3. Upload the optimized version back to storage
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Log the operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'optimize_pdf',
        status: 'completed',
        metadata: { processed_at: new Date().toISOString() }
      })
    
    return {
      success: true,
      document_id: document.id,
      operation: 'optimize_pdf',
      message: 'PDF optimization completed successfully'
    }
  } catch (error) {
    console.error(`Error optimizing PDF: ${error.message}`)
    
    // Log the failed operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'optimize_pdf',
        status: 'failed',
        metadata: { error: error.message }
      })
    
    throw error
  }
}

// Function to convert a document to PDF format
async function convertToPdf(supabase, document) {
  try {
    console.log(`Converting document to PDF: ${document.id}`)
    
    // In a real implementation, you would:
    // 1. Download the document from storage
    // 2. Use appropriate libraries to convert it to PDF
    // 3. Upload the PDF version back to storage
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2500))
    
    // Generate a filename for the PDF version
    const originalFilename = document.title || 'document'
    const pdfFilename = originalFilename.replace(/\.[^/.]+$/, '') + '.pdf'
    
    // Log the operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'convert_to_pdf',
        status: 'completed',
        metadata: { 
          original_filename: originalFilename,
          pdf_filename: pdfFilename,
          processed_at: new Date().toISOString() 
        }
      })
    
    return {
      success: true,
      document_id: document.id,
      operation: 'convert_to_pdf',
      pdf_filename: pdfFilename,
      message: 'Document conversion to PDF completed successfully'
    }
  } catch (error) {
    console.error(`Error converting to PDF: ${error.message}`)
    
    // Log the failed operation
    await supabase
      .from('document_operations')
      .insert({
        document_id: document.id,
        operation: 'convert_to_pdf',
        status: 'failed',
        metadata: { error: error.message }
      })
    
    throw error
  }
}
