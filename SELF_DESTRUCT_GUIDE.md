# Self-Destruct Messages - User Guide

## Overview
The Self-Destruct Messages feature automatically deletes all messages in your group after a custom time period that you set. This is perfect for:
- Privacy-focused groups
- Temporary discussions
- Sensitive information sharing
- Reducing chat clutter

---

## How to Configure

### Step 1: Access Self-Destruct Settings
1. Use `/settings` command in your group
2. Click **"💥 Self-Destruct"** button

### Step 2: Enable/Disable Feature
Click the **"✅ Enable/Disable"** button to toggle self-destruct messages ON or OFF

### Step 3: Set Deletion Time
You can customize the deletion timer with three components:

#### Set Hours (0-23)
- Click **"Set Hours"**
- Send a number between 0 and 23
- Example: `2` for 2 hours
- Send `/skip` for 0 hours
- Send `/cancel` to abort

#### Set Minutes (0-59)
- Click **"Set Minutes"**
- Send a number between 0 and 59
- Example: `30` for 30 minutes
- Send `/skip` for 0 minutes
- Send `/cancel` to abort

#### Set Seconds (5-59)
- Click **"Set Seconds"**
- Send a number between 5 and 59
- Example: `30` for 30 seconds
- **Minimum: 5 seconds** (recommended for proper functionality)
- Send `/skip` for default 30 seconds
- Send `/cancel` to abort

---

## Time Configuration Examples

### Example 1: Quick Delete (30 seconds)
```
Hours: 0 (or /skip)
Minutes: 0 (or /skip)
Seconds: 30
Total: 30 seconds
```

### Example 2: Short Discussion (5 minutes)
```
Hours: 0 (or /skip)
Minutes: 5
Seconds: 0 (or /skip)
Total: 5 minutes
```

### Example 3: Medium Duration (1 hour 30 minutes)
```
Hours: 1
Minutes: 30
Seconds: 0 (or /skip)
Total: 1 hour 30 minutes
```

### Example 4: Long Duration (24 hours)
```
Hours: 23
Minutes: 59
Seconds: 59
Total: 23 hours 59 minutes 59 seconds
```

### Example 5: Custom Mix (2 hours 15 minutes 45 seconds)
```
Hours: 2
Minutes: 15
Seconds: 45
Total: 2h 15m 45s
```

---

## How It Works

1. **Enable the feature** in settings
2. **Set your desired time** (hours, minutes, seconds)
3. **All new messages** sent to the group will be automatically deleted after the specified time
4. The bot schedules deletion immediately when a message is received
5. Messages are deleted silently without notification

---

## Important Notes

### ⚠️ Minimum Time Recommendation
- **Minimum: 5 seconds**
- Setting too low (< 5 seconds) may cause issues with message delivery
- Recommended: At least 10-30 seconds for reliable operation

### 📊 What Gets Deleted
- ✅ Regular text messages
- ✅ Photos and images
- ✅ Videos
- ✅ Documents/files
- ✅ Voice messages
- ✅ Stickers
- ✅ All message types

### ❌ What Doesn't Get Deleted
- System messages (member join/leave)
- Bot welcome/goodbye messages (these have their own settings)
- Messages sent before enabling the feature

### 🔒 Permissions Required
The bot needs:
- **Delete Messages** permission in the group
- Admin privileges to delete other users' messages

---

## Use Cases

### 1. Privacy-Focused Groups
```
Settings: 5 minutes
Perfect for: Sensitive discussions, confidential information
```

### 2. Temporary Announcements
```
Settings: 1 hour
Perfect for: Time-sensitive announcements, flash sales
```

### 3. Active Chat Rooms
```
Settings: 30 minutes
Perfect for: Reducing clutter, keeping chat fresh
```

### 4. Support Channels
```
Settings: 2 hours
Perfect for: Temporary support tickets, Q&A sessions
```

### 5. Event Discussions
```
Settings: 3 hours
Perfect for: Live event coverage, webinars
```

---

## Tips & Best Practices

### ✅ Do's
1. **Test with different times** - Find what works best for your group
2. **Inform members** - Let users know messages will auto-delete
3. **Use appropriate timing** - Match deletion time to your group's purpose
4. **Monitor performance** - Ensure bot has necessary permissions
5. **Combine with other features** - Works great with welcome messages

### ❌ Don'ts
1. **Don't set too low** - Below 5 seconds may cause issues
2. **Don't forget permissions** - Bot needs delete rights
3. **Don't use for important info** - Messages will be permanently deleted
4. **Don't enable unexpectedly** - Warn your community first

---

## Troubleshooting

### Issue: Messages not being deleted
**Solutions:**
1. Check if self-destruct is enabled in settings
2. Verify total time is not 0 (must have at least one value > 0)
3. Ensure bot has "Delete Messages" permission
4. Check bot is an admin in the group
5. Verify bot token has necessary permissions

### Issue: Deletion too fast/slow
**Solution:**
- Adjust hours/minutes/seconds in settings
- Remember: Total time = Hours + Minutes + Seconds
- Test with different values to find optimal timing

### Issue: Some messages not deleting
**Solutions:**
1. Bot may not have permission to delete certain message types
2. Very old messages won't be affected (only new ones after enabling)
3. System messages (join/leave) are excluded by design
4. Check bot logs for error messages

### Issue: Want to disable temporarily
**Solution:**
- Go to settings → Self-Destruct
- Click "Enable/Disable" button to toggle OFF
- Re-enable anytime with same button
- Your time settings are saved even when disabled

---

## Advanced Usage

### Combining with Other Features

#### Welcome Messages + Self-Destruct
```
Welcome Message: Enabled (permanent)
Self-Destruct: Enabled (30 minutes)
Result: Welcome stays, user messages delete
```

#### Goodbye Messages + Self-Destruct
```
Goodbye Message: Enabled (permanent)
Self-Destruct: Enabled (1 hour)
Result: Goodbye stays, chat messages delete
```

#### Anti-Spam + Self-Destruct
```
Anti-Spam: Enabled
Self-Destruct: Enabled (15 minutes)
Result: Spam blocked + messages auto-cleaned
```

### Time Presets (Recommended)

| Purpose | Hours | Minutes | Seconds | Total |
|---------|-------|---------|---------|-------|
| Ultra Fast | 0 | 0 | 10 | 10s |
| Quick Chat | 0 | 5 | 0 | 5m |
| Standard | 0 | 30 | 0 | 30m |
| Extended | 1 | 0 | 0 | 1h |
| Long Term | 6 | 0 | 0 | 6h |
| Daily | 23 | 59 | 59 | ~24h |

---

## FAQ

**Q: Can I exclude certain messages?**  
A: Currently, all user messages are deleted. System messages and bot messages (welcome/goodbye) are excluded by default.

**Q: Will deleted messages be recoverable?**  
A: No, deletion is permanent. Telegram doesn't provide a way to recover deleted messages.

**Q: Does this affect media files?**  
A: Yes, all message types including photos, videos, and documents are deleted.

**Q: Can users see when messages will be deleted?**  
A: No, there's no countdown visible to users. Messages simply disappear after the set time.

**Q: What happens if bot goes offline?**  
A: Messages scheduled for deletion while bot is offline may not be deleted until bot comes back online.

**Q: Is there a maximum time limit?**  
A: You can set up to 23 hours, 59 minutes, and 59 seconds. For longer periods, consider disabling the feature.

**Q: Does this work in supergroups?**  
A: Yes, works in both regular groups and supergroups.

**Q: Will this delete pinned messages?**  
A: Pinned messages can still be deleted by the bot if it has admin permissions. Consider unpinning important messages.

---

## Need Help?

If you experience issues:
1. Check bot permissions in group settings
2. Verify self-destruct is enabled
3. Ensure time is set correctly (not 0)
4. Review bot logs for errors
5. Test with a short duration first (e.g., 10 seconds)

Enjoy your self-cleaning group chat! 🎯
