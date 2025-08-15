export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { token } = req.body;

  if (!token) {
    return res.status(400).json({ error: 'Token required' });
  }

  try {
    // TODO: In production, validate token from database/KV store
    // For demo, accept any token that looks like a valid format
    if (token.length >= 16) {
      return res.status(200).json({ 
        success: true, 
        email: 'demo@rzero.com' // In production, return actual email from token
      });
    } else {
      return res.status(401).json({ error: 'Invalid or expired token' });
    }

  } catch (error) {
    console.error('Error validating token:', error);
    return res.status(500).json({ error: 'Validation failed' });
  }
}