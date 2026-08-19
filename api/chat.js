export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.GROQ_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: 'GROQ_API_KEY is missing in Vercel settings.' });
  }

  try {
    // Model ID update kar ke "llama-3.1-8b-instant" kar diya hai
    const { model = "llama-3.1-8b-instant", messages = [] } = req.body || {};

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey.trim()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: 0.7
      })
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({ 
        error: data.error?.message || "Groq API Error",
        raw: data
      });
    }

    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: 'Server Exception', details: err.message });
  }
}