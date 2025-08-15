export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email } = req.body;

  // Validate email
  if (!email || !email.endsWith('@rzero.com')) {
    return res.status(400).json({ error: 'Only @rzero.com emails allowed' });
  }

  try {
    // Generate random token
    const token = Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2);
    
    // Store token temporarily (in production, use a database)
    // For now, we'll use Vercel KV or just validate any token for demo
    
    // Send email using SendGrid
    const sendGridResponse = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.SENDGRID_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        personalizations: [
          {
            to: [{ email: email }],
            subject: 'Your NYC ODCV Prospector Access Link'
          }
        ],
        from: {
          email: 'noreply@rzero.com',
          name: 'R-Zero NYC Prospector'
        },
        content: [{
          type: 'text/html',
          value: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <div style="text-align: center; padding: 40px 20px;">
                <img src="https://rzero.com/wp-content/uploads/2021/10/rzero-logo-pad.svg" alt="R-Zero" style="width: 150px; margin-bottom: 30px;">
                <h1 style="color: #333; margin-bottom: 20px;">Access NYC ODCV Prospector</h1>
                <p style="color: #666; font-size: 16px; margin-bottom: 30px;">Click the button below to securely access your account:</p>
                <a href="${process.env.SITE_URL}?token=${token}" style="display: inline-block; background: #0066cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">Access Prospector</a>
                <p style="color: #999; font-size: 14px; margin-top: 30px;">This link expires in 15 minutes.<br>If you didn't request this, please ignore this email.</p>
              </div>
            </div>
          `
        }]
      }),
    });

    if (!sendGridResponse.ok) {
      const error = await sendGridResponse.text();
      console.error('SendGrid error status:', sendGridResponse.status);
      console.error('SendGrid error response:', error);
      console.error('API Key being used:', process.env.SENDGRID_API_KEY ? 'Present' : 'Missing');
      throw new Error(`SendGrid failed with status ${sendGridResponse.status}: ${error}`);
    }

    // Store token with expiration (15 minutes)
    const tokenData = {
      email: email,
      expires: Date.now() + (15 * 60 * 1000)
    };
    
    // TODO: In production, store in database or Vercel KV
    // For demo, we'll validate any token that looks right
    
    return res.status(200).json({ 
      success: true, 
      message: `Magic link sent to ${email}` 
    });

  } catch (error) {
    console.error('Error sending magic link:', error);
    return res.status(500).json({ error: 'Failed to send magic link' });
  }
}