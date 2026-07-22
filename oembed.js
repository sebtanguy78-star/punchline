export async function onRequest(context) {
  const url = new URL(context.request.url).searchParams.get('url');
  
  if (!url) {
    return new Response(JSON.stringify({ error: 'Missing url' }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }

  const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'application/json',
  };

  let thumbnail_url = null;
  let title = null;

  try {
    const decoded = decodeURIComponent(url);

    // ── TIKTOK ──
    if (decoded.includes('tiktok.com')) {
      try {
        const res = await fetch(`https://www.tiktok.com/oembed?url=${encodeURIComponent(decoded)}`, { headers: HEADERS });
        if (res.ok) { const d = await res.json(); thumbnail_url = d.thumbnail_url || null; title = d.title || null; }
      } catch {}
      if (!thumbnail_url) {
        try {
          const res = await fetch(`https://open.tiktok.com/oembed/?url=${encodeURIComponent(decoded)}`, { headers: HEADERS });
          if (res.ok) { const d = await res.json(); thumbnail_url = d.thumbnail_url || null; }
        } catch {}
      }

    // ── YOUTUBE ──
    } else if (decoded.includes('youtube.com') || decoded.includes('youtu.be')) {
      try {
        const res = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(decoded)}&format=json`, { headers: HEADERS });
        if (res.ok) { const d = await res.json(); thumbnail_url = d.thumbnail_url || null; title = d.title || null; }
      } catch {}
      if (!thumbnail_url) {
        const m = decoded.match(/(?:v=|youtu\.be\/)([A-Za-z0-9_-]{11})/);
        if (m) thumbnail_url = `https://img.youtube.com/vi/${m[1]}/hqdefault.jpg`;
      }
    }

  } catch (e) {}

  return new Response(JSON.stringify({ thumbnail_url, title }), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=86400'
    }
  });
}
