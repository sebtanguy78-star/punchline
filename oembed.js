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

    const HEADERS = {
      'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
      'Accept': 'application/json',
      'Referer': 'https://www.google.com/'
    };

    // ── TIKTOK ──
    if (decoded.includes('tiktok.com')) {
      // Essai 1 : API oEmbed officielle avec bon User-Agent
      try {
        const res = await fetch(
          `https://www.tiktok.com/oembed?url=${encodeURIComponent(decoded)}`,
          { headers: HEADERS }
        );
        if (res.ok) {
          const data = await res.json();
          thumbnail_url = data.thumbnail_url || null;
          title = data.title || null;
        }
      } catch {}

      // Essai 2 : API oEmbed via endpoint alternatif
      if (!thumbnail_url) {
        try {
          const res = await fetch(
            `https://open.tiktok.com/oembed/?url=${encodeURIComponent(decoded)}`,
            { headers: HEADERS }
          );
          if (res.ok) {
            const data = await res.json();
            thumbnail_url = data.thumbnail_url || null;
          }
        } catch {}
      }

      // Essai 3 : Extraire l'ID vidéo et construire une URL de miniature directe
      if (!thumbnail_url) {
        const match = decoded.match(/video\/(\d+)/);
        if (match) {
          const videoId = match[1];
          thumbnail_url = `https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/${videoId}`;
        }
      }

    // ── INSTAGRAM ──
    } else if (decoded.includes('instagram.com')) {
      const match = decoded.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
      if (match) {
        const shortcode = match[1];
        thumbnail_url = `https://www.instagram.com/p/${shortcode}/media/?size=l`;
        try {
          const check = await fetch(thumbnail_url, { method: 'HEAD', headers: HEADERS });
          if (!check.ok) thumbnail_url = null;
        } catch { thumbnail_url = null; }
      }

    // ── YOUTUBE ──
    } else if (decoded.includes('youtube.com') || decoded.includes('youtu.be')) {
      // YouTube oEmbed fiable
      try {
        const res = await fetch(
          `https://www.youtube.com/oembed?url=${encodeURIComponent(decoded)}&format=json`,
          { headers: HEADERS }
        );
        if (res.ok) {
          const data = await res.json();
          thumbnail_url = data.thumbnail_url || null;
          title = data.title || null;
        }
      } catch {}

      // Fallback : URL directe de la miniature YouTube
      if (!thumbnail_url) {
        const ytMatch = decoded.match(/(?:v=|youtu\.be\/)([A-Za-z0-9_-]{11})/);
        if (ytMatch) {
          thumbnail_url = `https://img.youtube.com/vi/${ytMatch[1]}/hqdefault.jpg`;
        }
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
