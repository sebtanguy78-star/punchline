exports.handler = async function(event) {
  const { url } = event.queryStringParameters || {};

  if (!url) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Missing url parameter' })
    };
  }

  let oembedUrl = null;

  try {
    const decoded = decodeURIComponent(url);

    if (decoded.includes('instagram.com')) {
      const token = process.env.INSTAGRAM_TOKEN;
      if (!token) {
        return {
          statusCode: 200,
          headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
          body: JSON.stringify({ thumbnail_url: null, title: null, error: 'No Instagram token configured' })
        };
      }
      oembedUrl = `https://graph.facebook.com/v18.0/instagram_oembed?url=${encodeURIComponent(decoded)}&maxwidth=400&access_token=${token}`;

    } else if (decoded.includes('tiktok.com')) {
      oembedUrl = `https://www.tiktok.com/oembed?url=${encodeURIComponent(decoded)}`;

    } else if (decoded.includes('youtube.com') || decoded.includes('youtu.be')) {
      oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(decoded)}&format=json`;

    } else {
      return {
        statusCode: 200,
        headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
        body: JSON.stringify({ thumbnail_url: null, title: null })
      };
    }

    const res = await fetch(oembedUrl);
    if (!res.ok) throw new Error('oEmbed fetch failed: ' + res.status);
    const data = await res.json();

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=86400'
      },
      body: JSON.stringify({
        thumbnail_url: data.thumbnail_url || null,
        title: data.title || null,
        author_name: data.author_name || null
      })
    };

  } catch (e) {
    return {
      statusCode: 200,
      headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
      body: JSON.stringify({ thumbnail_url: null, title: null, error: e.message })
    };
  }
};
