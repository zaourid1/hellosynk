<?php
/**
 * Plugin Name: HelloSynk OS Embed
 * Plugin URI: https://github.com/yourusername/hellosynk
 * Description: Embed HelloSynk OS demo in your WordPress pages
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://yourwebsite.com
 * License: MIT
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * HelloSynk Embed Shortcode
 * 
 * Usage: [hellosynk url="https://your-hellosynk-url.com" height="800px"]
 * 
 * @param array $atts Shortcode attributes
 * @return string HTML output
 */
function hellosynk_embed_shortcode($atts) {
    // Default attributes
    $atts = shortcode_atts(array(
        'url' => 'http://localhost:8000',
        'height' => '800px',
        'width' => '100%',
        'border' => '1px solid #ddd',
        'border_radius' => '8px',
    ), $atts, 'hellosynk');
    
    // Sanitize inputs
    $url = esc_url($atts['url']);
    $height = esc_attr($atts['height']);
    $width = esc_attr($atts['width']);
    $border = esc_attr($atts['border']);
    $border_radius = esc_attr($atts['border_radius']);
    
    // Generate unique ID for this embed
    $embed_id = 'hellosynk-' . uniqid();
    
    // Output HTML
    ob_start();
    ?>
    <div class="hellosynk-container" id="<?php echo esc_attr($embed_id); ?>" 
         style="width: <?php echo $width; ?>; 
                height: <?php echo $height; ?>; 
                border: <?php echo $border; ?>; 
                border-radius: <?php echo $border_radius; ?>; 
                overflow: hidden; 
                margin: 20px 0;
                position: relative;">
        <iframe 
            src="<?php echo $url; ?>" 
            width="100%" 
            height="100%" 
            frameborder="0"
            style="border: none; display: block;"
            allow="clipboard-read; clipboard-write; fullscreen"
            title="HelloSynk OS Demo"
            loading="lazy"
            id="<?php echo esc_attr($embed_id); ?>-iframe">
        </iframe>
        <style>
            #<?php echo esc_attr($embed_id); ?> {
                min-height: 600px;
            }
            @media (max-width: 768px) {
                #<?php echo esc_attr($embed_id); ?> {
                    height: 600px !important;
                }
            }
        </style>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('hellosynk', 'hellosynk_embed_shortcode');

/**
 * Add admin settings page
 */
function hellosynk_add_admin_menu() {
    add_options_page(
        'HelloSynk Settings',
        'HelloSynk',
        'manage_options',
        'hellosynk-settings',
        'hellosynk_settings_page'
    );
}
add_action('admin_menu', 'hellosynk_add_admin_menu');

/**
 * Settings page content
 */
function hellosynk_settings_page() {
    if (isset($_POST['hellosynk_save_settings'])) {
        check_admin_referer('hellosynk_settings');
        update_option('hellosynk_default_url', sanitize_text_field($_POST['hellosynk_url']));
        update_option('hellosynk_default_height', sanitize_text_field($_POST['hellosynk_height']));
        echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
    }
    
    $default_url = get_option('hellosynk_default_url', 'http://localhost:8000');
    $default_height = get_option('hellosynk_default_height', '800px');
    ?>
    <div class="wrap">
        <h1>HelloSynk OS Settings</h1>
        <form method="post" action="">
            <?php wp_nonce_field('hellosynk_settings'); ?>
            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="hellosynk_url">Default HelloSynk URL</label>
                    </th>
                    <td>
                        <input type="url" 
                               id="hellosynk_url" 
                               name="hellosynk_url" 
                               value="<?php echo esc_attr($default_url); ?>" 
                               class="regular-text"
                               placeholder="https://your-hellosynk-url.com">
                        <p class="description">Default URL to use when embedding HelloSynk OS</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">
                        <label for="hellosynk_height">Default Height</label>
                    </th>
                    <td>
                        <input type="text" 
                               id="hellosynk_height" 
                               name="hellosynk_height" 
                               value="<?php echo esc_attr($default_height); ?>" 
                               class="regular-text"
                               placeholder="800px">
                        <p class="description">Default height for the embed (e.g., 800px, 100vh)</p>
                    </td>
                </tr>
            </table>
            <p class="submit">
                <input type="submit" 
                       name="hellosynk_save_settings" 
                       class="button button-primary" 
                       value="Save Settings">
            </p>
        </form>
        
        <h2>Usage</h2>
        <p>Use the shortcode in your pages and posts:</p>
        <code>[hellosynk url="<?php echo esc_html($default_url); ?>" height="<?php echo esc_html($default_height); ?>"]</code>
        
        <h3>Shortcode Parameters</h3>
        <ul>
            <li><strong>url</strong> - The URL of your HelloSynk OS instance (default: from settings)</li>
            <li><strong>height</strong> - Height of the embed (default: 800px)</li>
            <li><strong>width</strong> - Width of the embed (default: 100%)</li>
            <li><strong>border</strong> - Border style (default: 1px solid #ddd)</li>
            <li><strong>border_radius</strong> - Border radius (default: 8px)</li>
        </ul>
    </div>
    <?php
}


