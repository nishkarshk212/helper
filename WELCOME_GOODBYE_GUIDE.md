# Custom Welcome & Goodbye Messages - User Guide

## Overview
Your Telegram bot now supports advanced custom welcome and goodbye messages with:
- **Multiple message types**: Text, Photo, Video, Document
- **Custom captions** with user mentions
- **Inline buttons** with custom URLs
- **Separate configuration** for welcome and goodbye messages

---

## How to Configure

### 1. Access Settings
Use `/settings` command in your group (admin only)

### 2. Enable Messages
- Click **"✅ Welcome Messages"** to toggle welcome messages ON/OFF
- Click **"✅ Goodbye Messages"** to toggle goodbye messages ON/OFF

### 3. Configure Welcome Message

#### Step 1: Choose Message Type
Click **"📝 Edit Welcome Message"** and select:
- **Text** - Simple text message
- **Photo** - Image with caption
- **Video** - Video with caption
- **Document** - File/document with caption

#### Step 2A: For Text Messages
1. Send your welcome message text
2. Use `{user}` to mention the new member
3. Example: `Welcome {user} to our amazing community! 🎉`

#### Step 2B: For Media Messages (Photo/Video/Document)
1. Send the media file (photo, video, or document)
2. After sending media, send the caption text
3. Use `{user}` to mention the new member
4. Or send `/skip` for no caption

#### Step 3: Add Inline Buttons (Optional)
After setting the message, you'll be asked about buttons:
- Click **"Add Buttons"** to add custom inline buttons
- Send buttons in this format (one per line):
  ```
  Button Text - URL
  ```
- Example:
  ```
  📢 Channel - https://t.me/yourchannel
  📜 Rules - https://example.com/rules
  💬 Support - https://t.me/support
  ```
- Click **"Skip"** to continue without buttons

---

### 4. Configure Goodbye Message

The process is identical to welcome messages:
1. Click **"👋 Edit Goodbye Message"**
2. Select message type (Text/Photo/Video/Document)
3. Set the message/caption
4. Use `{user}` to mention the leaving member
5. Add optional inline buttons

Example goodbye message:
```
Goodbye {user}! We'll miss you. Feel free to rejoin anytime! 👋
```

---

## Usage Examples

### Example 1: Simple Text Welcome
```
Settings → Edit Welcome Message → Text
Message: "Hey {user}! Welcome to the group! 🎊"
Buttons: Skip
```

### Example 2: Photo Welcome with Buttons
```
Settings → Edit Welcome Message → Photo
Send: [Upload a welcome image]
Caption: "Welcome {user}! Please read the rules."
Buttons:
  📖 Read Rules - https://telegra.ph/rules
  🎮 Games Channel - https://t.me/games
```

### Example 3: Video Welcome with Multiple Buttons
```
Settings → Edit Welcome Message → Video
Send: [Upload welcome video]
Caption: "Hi {user}! Watch this quick intro!"
Buttons:
  🔔 Notifications - https://t.me/notifications
  💡 Tips - https://example.com/tips
  ❓ FAQ - https://example.com/faq
  🌐 Website - https://example.com
```

### Example 4: Goodbye with Rejoin Button
```
Settings → Edit Goodbye Message → Text
Message: "Sad to see you go, {user}! Hope to see you again! 😢"
Buttons:
  🔄 Rejoin Group - https://t.me/yourgroup
```

---

## Button Format Rules

✅ **Correct Format:**
```
Button Label - https://example.com
Another Button - https://t.me/channel
```

❌ **Incorrect Formats:**
```
Button Label: https://example.com  (Wrong separator)
https://example.com  (Missing label)
Button Label  (Missing URL)
```

**Important:**
- Use ` - ` (space-dash-space) as separator
- One button per line
- Maximum buttons per row: Telegram handles layout automatically
- URLs must be valid (start with http:// or https://)

---

## Placeholders

Use these placeholders in your messages:
- `{user}` - Mentions the new/leaving member

Example:
```
Welcome {user}! You are member number 100! 🎉
Goodbye {user}! Thanks for being part of our community!
```

---

## Tips & Best Practices

1. **Keep messages concise** - Long messages may be truncated
2. **Use emojis** - Makes messages more engaging 🎨
3. **Test your buttons** - Make sure URLs work correctly
4. **Media size limits** - Follow Telegram's file size restrictions
5. **Welcome both text and media** - Use text for simple greetings, media for rich experiences
6. **Goodbye messages are optional** - Enable only if you want to track departures

---

## Troubleshooting

### Issue: Media not sending
**Solution:** 
- Make sure you uploaded the media AFTER selecting the type
- Check if the file size is within Telegram limits
- Try using a different file format

### Issue: Buttons not appearing
**Solution:**
- Ensure you used the correct format: `Text - URL`
- Check that URLs are valid and complete
- Verify you clicked "Add Buttons" not "Skip"

### Issue: {user} not mentioning
**Solution:**
- Make sure you're using exact syntax: `{user}` (with curly braces)
- Don't add spaces inside the braces

### Issue: Settings not saving
**Solution:**
- Ensure you're an admin in the group
- Complete the entire configuration flow
- Don't send `/cancel` unless you want to abort

---

## Advanced Features

### Multiple Button Rows
The bot automatically arranges buttons. Each button you add creates a new row for better visibility.

### Mixed Media Types
You can use different types for welcome and goodbye:
- Welcome: Photo with buttons
- Goodbye: Simple text message

### Updating Configuration
To change any setting:
1. Go to `/settings`
2. Click the appropriate edit button
3. Follow the configuration steps again
4. New settings replace old ones immediately

---

## Need Help?

If you encounter issues:
1. Check this guide for common solutions
2. Ensure your bot has proper permissions in the group
3. Verify the bot token is correctly configured
4. Check bot logs for error messages

Enjoy your enhanced group management experience! 🚀
