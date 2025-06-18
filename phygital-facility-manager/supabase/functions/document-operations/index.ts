// Document Operations Edge Function
// Handles PDF generation, document conversion, text extraction, and summary generation
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.7.1';
import { Configuration, OpenAIApi } from "https://esm.sh/openai@3.1.0";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client with service role key for internal operations
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Initialize OpenAI API
    const openaiKey = Deno.env.get("OPENAI_API_KEY") || '';
    const configuration = new Configuration({ apiKey: openaiKey });
    const openai = new OpenAIApi(configuration);

    // Parse request body
    const { operation, documentId, userId, options } = await req.json();

    // Log operation start
    const logOperation = await supabase
      .from('document_operations')
      .insert({
        document_id: documentId,
        operation: operation,
        status: 'processing',
        created_by: userId,
        metadata: { started_at: new Date().toISOString() }
      })
      .select()
      .single();

    const operationId = logOperation.data?.id;
    let result = null;

    // Get document details
    const { data: document, error: documentError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', documentId)
      .single();

    if (documentError || !document) {
      throw new Error(`Document not found: ${documentError?.message || 'unknown error'}`);
    }

    // Get document file from storage
    const { data: fileData, error: fileError } = await supabase
      .storage
      .from('documents')
      .download(document.file_path);

    if (fileError || !fileData) {
      throw new Error(`File download failed: ${fileError?.message || 'unknown error'}`);
    }

    // Handle different operations
    switch (operation) {
      case 'extract_text':
        result = await extractText(fileData, document, supabase);
        break;

      case 'generate_summary':
        result = await generateSummary(fileData, document, openai, supabase);
        break;

      case 'convert_to_pdf':
        result = await convertToPdf(fileData, document, supabase);
        break;

      case 'optimize_pdf':
        result = await optimizePdf(fileData, document, supabase);
        break;

      default:
        throw new Error(`Unsupported operation: ${operation}`);
    }

    // Update operation log with success
    await supabase
      .from('document_operations')
      .update({
        status: 'success',
        metadata: {
          ...logOperation.data?.metadata,
          completed_at: new Date().toISOString(),
          result
        }
      })
      .eq('id', operationId);

    // Return success response
    return new Response(
      JSON.stringify({
        success: true,
        operation: operation,
        documentId: documentId,
        result: result
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    );

  } catch (error) {
    console.error('Error processing document operation:', error);

    // Return error response
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});

// Text extraction function
async function extractText(fileData, document, supabase) {
  // TODO: Replace this simulation with actual PDF text extraction
  // For now, we'll simulate text extraction for demo purposes
  const textContent = `This is simulated extracted text content for document ${document.title}.
  
In a real implementation, we would use a PDF parsing library like pdf.js or a PDF-to-text service to extract the actual content of the document.

The extracted text would contain all the textual content from the PDF file, which could then be used for searching, indexing, or further processing like summarization.`;

  // Update document with extracted text
  await supabase
    .from('documents')
    .update({
      text_content: textContent,
      updated_at: new Date().toISOString()
    })
    .eq('id', document.id);

  return {
    message: 'Text extracted successfully',
    characterCount: textContent.length
  };
}

// Summary generation function using OpenAI
async function generateSummary(fileData, document, openai, supabase) {
  // Get document text content or extract it if not available
  let textContent = document.text_content;
  
  if (!textContent) {
    const extractResult = await extractText(fileData, document, supabase);
    
    // Get updated document with text content
    const { data: updatedDocument } = await supabase
      .from('documents')
      .select('text_content')
      .eq('id', document.id)
      .single();
      
    textContent = updatedDocument.text_content;
  }
  
  // Trim text if needed (OpenAI has token limits)
  const MAX_CHARS = 15000;
  const trimmedText = textContent.length > MAX_CHARS 
    ? textContent.substring(0, MAX_CHARS) + "..."
    : textContent;

  // Generate summary using OpenAI
  const response = await openai.createCompletion({
    model: "text-davinci-003", // or use a more current model
    prompt: `Please provide a concise summary of the following document:\n\n${trimmedText}`,
    max_tokens: 500,
    temperature: 0.5,
  });

  const summary = response.data.choices[0].text.trim();

  // Update document with summary
  await supabase
    .from('documents')
    .update({
      summary: summary,
      updated_at: new Date().toISOString()
    })
    .eq('id', document.id);

  return {
    message: 'Summary generated successfully',
    summaryLength: summary.length
  };
}

// PDF conversion function
async function convertToPdf(fileData, document, supabase) {
  // TODO: Replace this simulation with actual document-to-PDF conversion
  // This would typically use a service like LibreOffice, Pandoc, or a cloud conversion API
  
  const fileName = document.title.replace(/[^a-zA-Z0-9]/g, '_') + '.pdf';
  const filePath = `converted/${document.id}/${fileName}`;
  
  // Simulate a PDF file (in real implementation, use actual conversion)
  const simulatedPdfData = fileData; // In real implementation, this would be converted data
  
  // Upload "converted" PDF to storage
  const { data: uploadData, error: uploadError } = await supabase
    .storage
    .from('documents')
    .upload(filePath, simulatedPdfData, {
      contentType: 'application/pdf',
      upsert: true
    });
    
  if (uploadError) {
    throw new Error(`PDF upload failed: ${uploadError.message}`);
  }
  
  // Get the public URL
  const { data: publicUrlData } = await supabase
    .storage
    .from('documents')
    .getPublicUrl(filePath);
    
  const pdfUrl = publicUrlData.publicUrl;
  
  // Track conversion in database
  const { data: conversionData } = await supabase
    .from('document_versions')
    .insert({
      document_id: document.id,
      version_type: 'pdf_conversion',
      file_path: filePath,
      file_name: fileName,
      file_size: simulatedPdfData.size,
      file_type: 'application/pdf'
    })
    .select()
    .single();

  return {
    message: 'Document converted to PDF successfully',
    url: pdfUrl,
    versionId: conversionData.id
  };
}

// PDF optimization function 
async function optimizePdf(fileData, document, supabase) {
  // TODO: Replace this simulation with actual PDF optimization
  // This would typically use a PDF library or service to compress and optimize the PDF
  
  const fileName = document.title.replace(/[^a-zA-Z0-9]/g, '_') + '_optimized.pdf';
  const filePath = `optimized/${document.id}/${fileName}`;
  
  // Simulate an optimized PDF file (in real implementation, use actual optimization)
  const simulatedOptimizedData = fileData; // In real implementation, this would be optimized data
  
  // Upload "optimized" PDF to storage
  const { data: uploadData, error: uploadError } = await supabase
    .storage
    .from('documents')
    .upload(filePath, simulatedOptimizedData, {
      contentType: 'application/pdf',
      upsert: true
    });
    
  if (uploadError) {
    throw new Error(`Optimized PDF upload failed: ${uploadError.message}`);
  }
  
  // Get the public URL
  const { data: publicUrlData } = await supabase
    .storage
    .from('documents')
    .getPublicUrl(filePath);
    
  const pdfUrl = publicUrlData.publicUrl;
  
  // Track optimization in database
  const { data: optimizationData } = await supabase
    .from('document_versions')
    .insert({
      document_id: document.id,
      version_type: 'pdf_optimized',
      file_path: filePath,
      file_name: fileName,
      file_size: simulatedOptimizedData.size, // In real impl, would be smaller than original
      file_type: 'application/pdf'
    })
    .select()
    .single();

  return {
    message: 'PDF optimized successfully',
    url: pdfUrl,
    versionId: optimizationData.id,
    // In a real implementation, we would return optimization stats:
    // originalSize: fileData.size,
    // optimizedSize: simulatedOptimizedData.size,
    // reductionPercentage: (1 - simulatedOptimizedData.size / fileData.size) * 100
  };
}
