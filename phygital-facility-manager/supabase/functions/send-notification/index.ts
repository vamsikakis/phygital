// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

console.log("Email notification edge function initiated")

// Google OAuth2 client setup
const GOOGLE_CLIENT_ID = Deno.env.get('GOOGLE_CLIENT_ID') ?? ''
const GOOGLE_CLIENT_SECRET = Deno.env.get('GOOGLE_CLIENT_SECRET') ?? ''
const REFRESH_TOKEN = Deno.env.get('GMAIL_REFRESH_TOKEN') ?? ''

// Templates for common notifications
const EMAIL_TEMPLATES = {
  announcement: {
    subject: "New Announcement: {{title}}",
    body: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>New Announcement</h2>
        <h3>{{title}}</h3>
        <div style="padding: 15px; background-color: #f7f7f7; border-radius: 5px;">
          <p>{{content}}</p>
        </div>
        <p style="margin-top: 20px;">Date: {{date}}</p>
        <p>Priority: {{priority}}</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
          This is an automated message from the Gopalan Atlantis Facility Management System.
          Please do not reply directly to this email.
        </p>
      </div>
    `
  },
  event: {
    subject: "Upcoming Event: {{title}}",
    body: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Upcoming Event</h2>
        <h3>{{title}}</h3>
        <div style="padding: 15px; background-color: #f7f7f7; border-radius: 5px;">
          <p>{{description}}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Date:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{date}}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Time:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{time_start}} - {{time_end}}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Location:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{location}}</td>
          </tr>
        </table>
        <hr>
        <p style="font-size: 12px; color: #666;">
          This is an automated message from the Gopalan Atlantis Facility Management System.
          Please do not reply directly to this email.
        </p>
      </div>
    `
  },
  ticket_update: {
    subject: "Ticket Update: {{subject}} [#{{ticket_id}}]",
    body: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Your Ticket Has Been Updated</h2>
        <h3>{{subject}}</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Ticket ID:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">#{{ticket_id}}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{status}}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Last Updated:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{last_updated}}</td>
          </tr>
        </table>
        <div style="padding: 15px; background-color: #f7f7f7; border-radius: 5px; margin-top: 20px;">
          <p><strong>Latest Comment:</strong></p>
          <p>{{comment}}</p>
        </div>
        <p style="margin-top: 20px;">
          <a href="{{ticket_url}}" style="background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">View Ticket</a>
        </p>
        <hr>
        <p style="font-size: 12px; color: #666;">
          This is an automated message from the Gopalan Atlantis Facility Management System.
          Please do not reply directly to this email.
        </p>
      </div>
    `
  },
  document_uploaded: {
    subject: "New Document Available: {{title}}",
    body: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>New Document Available</h2>
        <h3>{{title}}</h3>
        <div style="padding: 15px; background-color: #f7f7f7; border-radius: 5px;">
          <p>{{description}}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Category:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{category}}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Uploaded:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{created_at}}</td>
          </tr>
        </table>
        <p style="margin-top: 20px;">
          <a href="{{download_url}}" style="background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">Download Document</a>
        </p>
        <hr>
        <p style="font-size: 12px; color: #666;">
          This is an automated message from the Gopalan Atlantis Facility Management System.
          Please do not reply directly to this email.
        </p>
      </div>
    `
  }
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { notification_type, data, recipients, send_to_all } = await req.json()
    
    if (!notification_type || !data) {
      return new Response(
        JSON.stringify({ error: 'notification_type and data are required' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }
    
    // Create Supabase client with Admin privileges
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    // Get template for the notification type
    const template = EMAIL_TEMPLATES[notification_type]
    if (!template) {
      return new Response(
        JSON.stringify({ error: `Invalid notification type: ${notification_type}` }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }
    
    // Prepare email content
    const subject = replaceTokens(template.subject, data)
    const body = replaceTokens(template.body, data)
    
    // Get recipients
    let emailRecipients = []
    
    if (send_to_all) {
      // Send to all users
      const { data: users, error: usersError } = await supabaseClient
        .from('users')
        .select('email')
      
      if (usersError) {
        throw new Error(`Error fetching users: ${usersError.message}`)
      }
      
      emailRecipients = users.map(user => user.email)
    } else if (recipients && recipients.length > 0) {
      // Use provided recipient list
      emailRecipients = recipients
    } else {
      throw new Error('No recipients specified')
    }
    
    // Send emails
    const results = []
    for (const recipient of emailRecipients) {
      try {
        const result = await sendEmail(recipient, subject, body)
        results.push({ email: recipient, sent: true, result })
        
        // Log the notification
        await supabaseClient
          .from('notification_logs')
          .insert({
            notification_type,
            recipient,
            subject,
            status: 'sent',
            metadata: { data }
          })
      } catch (error) {
        results.push({ email: recipient, sent: false, error: error.message })
        
        // Log the failed notification
        await supabaseClient
          .from('notification_logs')
          .insert({
            notification_type,
            recipient,
            subject,
            status: 'failed',
            metadata: { error: error.message, data }
          })
      }
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        recipients_count: emailRecipients.length,
        results
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

// Function to replace template tokens with actual data
function replaceTokens(template, data) {
  let result = template
  
  for (const [key, value] of Object.entries(data)) {
    const token = `{{${key}}}`
    result = result.replace(new RegExp(token, 'g'), String(value))
  }
  
  return result
}

// Function to send an email using Gmail API
async function sendEmail(to, subject, body) {
  try {
    // First, get an access token using the refresh token
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        client_id: GOOGLE_CLIENT_ID,
        client_secret: GOOGLE_CLIENT_SECRET,
        refresh_token: REFRESH_TOKEN,
        grant_type: 'refresh_token'
      })
    })
    
    const tokenData = await tokenResponse.json()
    
    if (!tokenData.access_token) {
      throw new Error('Failed to get access token')
    }
    
    // Prepare the email
    const email = [
      'Content-Type: text/html; charset="UTF-8"',
      'MIME-Version: 1.0',
      `To: ${to}`,
      'From: Gopalan Atlantis Facility Management <notifications@gopalanatlantis.com>',
      `Subject: ${subject}`,
      '',
      body
    ].join('\r\n')
    
    // Encode the email in base64 URL format
    const base64EncodedEmail = btoa(email)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '')
    
    // Send the email using Gmail API
    const response = await fetch('https://www.googleapis.com/gmail/v1/users/me/messages/send', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenData.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        raw: base64EncodedEmail
      })
    })
    
    const result = await response.json()
    
    if (result.error) {
      throw new Error(`Gmail API error: ${result.error.message}`)
    }
    
    return result
  } catch (error) {
    console.error(`Error sending email to ${to}: ${error.message}`)
    throw error
  }
}
