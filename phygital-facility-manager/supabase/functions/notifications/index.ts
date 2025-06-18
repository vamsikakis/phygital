// Notifications Edge Function
// Handles sending email notifications for announcements, events, tickets, and general notifications
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.7.1';
import { corsHeaders } from '../_shared/cors.ts';

// Gmail API integration
import { google } from "https://deno.land/x/googleapis@v60.0.0/build/src/googleapis.ts";

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client with service role key for database operations
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Parse request body
    const { 
      notificationType, 
      recipients, 
      subject, 
      content,
      sourceId,
      userId, // The user sending the notification
      attachments = [],
      metadata = {}
    } = await req.json();

    if (!notificationType || !recipients || !subject || !content) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      );
    }

    // Log notification request
    const { data: logData, error: logError } = await supabase
      .from('notification_logs')
      .insert({
        notification_type: notificationType,
        recipients: recipients,
        subject: subject,
        source_id: sourceId,
        content: content,
        status: 'processing',
        created_by: userId,
        metadata: metadata
      })
      .select()
      .single();

    if (logError) {
      throw new Error(`Failed to log notification: ${logError.message}`);
    }

    const notificationId = logData.id;

    // Setup Gmail API
    const auth = new google.auth.OAuth2(
      Deno.env.get('GOOGLE_CLIENT_ID'),
      Deno.env.get('GOOGLE_CLIENT_SECRET')
    );

    // Use refresh token to get access token
    const refreshToken = Deno.env.get('GOOGLE_REFRESH_TOKEN');
    auth.setCredentials({ refresh_token: refreshToken });

    // Create Gmail service
    const gmail = google.gmail({ version: 'v1', auth });

    // Get sender info from environment or database
    const senderName = Deno.env.get('EMAIL_SENDER_NAME') || 'Gopalan Atlantis';
    const senderEmail = Deno.env.get('EMAIL_SENDER_ADDRESS') || 'no-reply@gopalanatlantis.com';

    // Prepare email content based on notification type
    const emailHtml = await prepareEmailTemplate(notificationType, subject, content, metadata);

    // Send emails to each recipient
    const sendPromises = [];
    let successCount = 0;
    let failedRecipients = [];

    for (const recipientEmail of recipients) {
      try {
        const message = createEmail(senderName, senderEmail, recipientEmail, subject, emailHtml, attachments);
        
        // Send email using Gmail API
        const response = await gmail.users.messages.send({
          userId: 'me',
          requestBody: {
            raw: message
          }
        });

        if (response.status === 200) {
          successCount++;
        } else {
          failedRecipients.push(recipientEmail);
        }
      } catch (err) {
        console.error(`Failed to send email to ${recipientEmail}:`, err);
        failedRecipients.push(recipientEmail);
      }
    }

    // Update notification log
    const status = failedRecipients.length > 0 
      ? (successCount > 0 ? 'partial' : 'failed') 
      : 'sent';
      
    await supabase
      .from('notification_logs')
      .update({
        status: status,
        metadata: {
          ...metadata,
          sent_count: successCount,
          failed_recipients: failedRecipients,
          sent_at: new Date().toISOString()
        }
      })
      .eq('id', notificationId);

    // Return success response
    return new Response(
      JSON.stringify({
        success: true,
        notification_id: notificationId,
        sent_count: successCount,
        failed_recipients: failedRecipients,
        status: status
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    );

  } catch (error) {
    console.error('Error sending notification:', error);

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

// Helper function to create email with proper formatting
function createEmail(senderName, senderEmail, to, subject, htmlContent, attachments = []) {
  // Email headers
  const headers = [
    `From: ${senderName} <${senderEmail}>`,
    `To: ${to}`,
    `Subject: ${subject}`,
    'MIME-Version: 1.0',
    'Content-Type: multipart/mixed; boundary="boundary_mixed"',
    '',
    '--boundary_mixed',
    'Content-Type: multipart/alternative; boundary="boundary_alternative"',
    '',
    '--boundary_alternative',
    'Content-Type: text/plain; charset=UTF-8',
    '',
    // Plain text version of the email (simplified version of HTML content)
    stripHtml(htmlContent),
    '',
    '--boundary_alternative',
    'Content-Type: text/html; charset=UTF-8',
    '',
    // HTML version of the email
    htmlContent,
    '',
    '--boundary_alternative--'
  ];

  // Add attachments if any
  for (let i = 0; i < attachments.length; i++) {
    const attachment = attachments[i];
    headers.push('');
    headers.push(`--boundary_mixed`);
    headers.push(`Content-Type: ${attachment.mimeType}; name="${attachment.filename}"`);
    headers.push('Content-Transfer-Encoding: base64');
    headers.push(`Content-Disposition: attachment; filename="${attachment.filename}"`);
    headers.push('');
    headers.push(attachment.content); // Base64 encoded content
  }

  headers.push('');
  headers.push('--boundary_mixed--');

  // Encode the email in base64
  const email = headers.join('\r\n');
  return btoa(email).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// Helper function to strip HTML tags for plain text email
function stripHtml(html) {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// Function to prepare email template based on notification type
async function prepareEmailTemplate(notificationType, subject, content, metadata) {
  const baseTemplate = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${subject}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          line-height: 1.6;
          color: #333;
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
        }
        .header {
          background-color: #0056b3;
          color: white;
          padding: 20px;
          text-align: center;
          border-radius: 5px 5px 0 0;
        }
        .content {
          padding: 20px;
          background-color: #f9f9f9;
          border: 1px solid #ddd;
          border-top: none;
          border-radius: 0 0 5px 5px;
        }
        .footer {
          text-align: center;
          margin-top: 20px;
          font-size: 12px;
          color: #777;
        }
        .button {
          display: inline-block;
          background-color: #0056b3;
          color: white;
          padding: 12px 20px;
          text-decoration: none;
          border-radius: 4px;
          margin: 15px 0;
        }
        .details {
          margin: 15px 0;
          padding: 10px;
          background-color: #fff;
          border-left: 4px solid #0056b3;
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>Gopalan Atlantis</h2>
        <h3>${subject}</h3>
      </div>
      <div class="content">
  `;

  let specificContent = '';
  let footerContent = '';

  // Customize the email content based on notification type
  switch (notificationType) {
    case 'announcement':
      specificContent = `
        <p>Dear Resident,</p>
        <div class="details">
          ${content}
        </div>
        <p>For more information, please log in to the Gopalan Atlantis Facility Manager application.</p>
      `;
      break;
      
    case 'event':
      specificContent = `
        <p>Dear Resident,</p>
        <h4>Event Details:</h4>
        <div class="details">
          ${content}
        </div>
        ${metadata.eventDate ? `<p><strong>Date:</strong> ${metadata.eventDate}</p>` : ''}
        ${metadata.eventTime ? `<p><strong>Time:</strong> ${metadata.eventTime}</p>` : ''}
        ${metadata.eventLocation ? `<p><strong>Location:</strong> ${metadata.eventLocation}</p>` : ''}
        <p>We look forward to your participation!</p>
        ${metadata.rsvpLink ? `<a href="${metadata.rsvpLink}" class="button">RSVP Now</a>` : ''}
      `;
      break;
      
    case 'ticket':
      specificContent = `
        <p>Dear Resident,</p>
        <h4>Ticket Update:</h4>
        <div class="details">
          <p><strong>Ticket #:</strong> ${metadata.ticketId || 'N/A'}</p>
          <p><strong>Status:</strong> ${metadata.status || 'Updated'}</p>
          <p><strong>Update:</strong> ${content}</p>
        </div>
        <p>For more details or to respond, please log in to the Gopalan Atlantis Facility Manager application.</p>
      `;
      break;
      
    default:
      specificContent = `
        <p>Dear Resident,</p>
        <div class="details">
          ${content}
        </div>
      `;
  }

  // Common footer
  footerContent = `
        <p>Thank you,<br>
        Gopalan Atlantis Management</p>
      </div>
      <div class="footer">
        <p>This is an automated message from Gopalan Atlantis Facility Management System.<br>
        Please do not reply directly to this email.</p>
        <p>If you need assistance, please contact the management office or submit a help request through the application.</p>
      </div>
    </body>
    </html>
  `;

  return baseTemplate + specificContent + footerContent;
}
