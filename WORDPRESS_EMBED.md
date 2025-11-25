# Embedding HelloSynk OS in WordPress

## Option 1: Iframe Embed (Easiest)

### Step 1: Make Your Server Accessible

You have two options:

#### A. Deploy to a Public Server
- Deploy HelloSynk to a cloud service (Heroku, Railway, Render, etc.)
- Or use a VPS with a public IP
- Make sure the server is accessible via HTTPS

#### B. Use a Tunnel Service (For Testing/Demo)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start your HelloSynk server
hellosynk web --host 0.0.0.0 --port 8000

# In another terminal, create a tunnel
ngrok http 8000
```

This will give you a public URL like: `https://abc123.ngrok.io`

### Step 2: Add to WordPress

#### Method A: Using Custom HTML Block

1. Go to your WordPress page editor
2. Add a "Custom HTML" block
3. Paste this code:

```html
<div style="width: 100%; height: 800px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
    <iframe 
        src="YOUR_HELLOSYNK_URL" 
        width="100%" 
        height="100%" 
        frameborder="0"
        style="border: none;"
        allow="clipboard-read; clipboard-write"
        title="HelloSynk OS Demo">
    </iframe>
</div>
```

Replace `YOUR_HELLOSYNK_URL` with your actual server URL.

#### Method B: Using Shortcode (Requires Plugin)

Add this to your theme's `functions.php` or create a simple plugin:

```php
function hellosynk_embed_shortcode($atts) {
    $atts = shortcode_atts(array(
        'url' => 'http://localhost:8000',
        'height' => '800px',
        'width' => '100%'
    ), $atts);
    
    return '<div style="width: ' . esc_attr($atts['width']) . '; height: ' . esc_attr($atts['height']) . '; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 20px 0;">
        <iframe 
            src="' . esc_url($atts['url']) . '" 
            width="100%" 
            height="100%" 
            frameborder="0"
            style="border: none;"
            allow="clipboard-read; clipboard-write"
            title="HelloSynk OS Demo">
        </iframe>
    </div>';
}
add_shortcode('hellosynk', 'hellosynk_embed_shortcode');
```

Then use in your page: `[hellosynk url="YOUR_URL" height="800px"]`

## Option 2: Standalone Embeddable Version

For a more integrated experience, you can create a standalone version that embeds directly in WordPress without an iframe. This requires extracting the HTML/CSS/JS and hosting it separately or embedding it directly.

## Option 3: WordPress Plugin

Create a full WordPress plugin that:
- Manages the HelloSynk connection
- Provides a settings page
- Renders the UI directly in WordPress

Would you like me to create any of these options?

## Security Considerations

1. **HTTPS Required**: Always use HTTPS for production
2. **API Keys**: Don't expose API keys in the frontend
3. **Rate Limiting**: Implement rate limiting on your server
4. **Authentication**: Consider adding authentication for production use

## Responsive Design

The iframe will be responsive. For mobile optimization, you can add:

```html
<div style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
    <iframe 
        src="YOUR_HELLOSYNK_URL" 
        width="100%" 
        height="100%" 
        frameborder="0"
        style="border: none;"
        allow="clipboard-read; clipboard-write"
        title="HelloSynk OS Demo"
        loading="lazy">
    </iframe>
</div>

<style>
@media (max-width: 768px) {
    .hellosynk-container {
        height: 600px !important;
    }
}
</style>
```

