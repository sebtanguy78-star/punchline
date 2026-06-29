exports.handler = async function(event) {
  const { url } = event.queryStringParameters || {};

  if (!url) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Missing url parameter' })
    };
  }

  try {
    const decoded = decodeURIComponent(url);
    let thumbnail_url = null;
    let title = null;

    // ── TIKTOK ──
    if (decoded.includes('tiktok.com')) {
      const res = await fetch(`https://www.tiktok.com/oembed?url=${encodeURIComponent(decoded)}`);
      if (res.ok) {
        const data = await res.json();
        thumbnail_url = data.thumbnail_url || null;
        title = data.title || null;
      }

    // ── INSTAGRAM ──
    } else if (decoded.includes('instagram.com')) {
      // Extraire le shortcode du lien instagram
      const match = decoded.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
      if (match) {
        const shortcode = match[1];
        // Essayer l'API image directe
        thumbnail_url = `https://www.instagram.com/p/${shortcode}/media/?size=l`;
        // Vérifier que l'image est accessible
        const check = await fetch(thumbnail_url, { method: 'HEAD' });
        if (!check.ok) thumbnail_url = null;
      }

    // ── YOUTUBE ──
    } else if (decoded.includes('youtube.com') || decoded.includes('youtu.be')) {
      const res = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(decoded)}&format=json`);
      if (res.ok) {
        const data = await res.json();
        thumbnail_url = data.thumbnail_url || null;
        title = data.title || null;
      }
    }

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=86400'
      },
      body: JSON.stringify({ thumbnail_url, title })
    };

  } catch (e) {
    return {
      statusCode: 200,
      headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
      body: JSON.stringify({ thumbnail_url: null, title: null, error: e.message })
    };
  }
};
