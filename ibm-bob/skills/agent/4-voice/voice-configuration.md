# Voice Configuration Guide

## Overview
Complete guide for configuring Speech-to-Text (STT), Text-to-Speech (TTS), and audio parameters for voice-enabled agents in watsonx Orchestrate.

## Voice Configuration Basics

Voice configurations control:
- **STT (Speech-to-Text)**: Converting user speech to text
- **TTS (Text-to-Speech)**: Converting agent responses to speech
- **Audio Parameters**: Sample rate, encoding, channels

**Always search ADK documentation before creating voice configurations.**

## YAML Specification

Voice configurations use YAML files with `spec_version: v1`.

### Required Fields
- `spec_version`: Must be "v1"
- `kind`: Must be "VoiceConfiguration"
- `name`: Unique identifier for the configuration
- `description`: Human-readable description
- `stt_provider`: Speech-to-Text provider configuration
- `tts_provider`: Text-to-Speech provider configuration

### Optional Fields
- `audio_config`: Audio quality and format settings
- `language_config`: Language-specific settings

### Template
```yaml
spec_version: v1
kind: VoiceConfiguration
name: my-voice-config
description: Voice configuration for customer service agent

stt_provider:
  provider: watson_stt
  model: en-US_Telephony
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: en-US_MichaelV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 8000
  encoding: mulaw
  channels: 1
```

## STT Providers

### Watson Speech to Text
**Provider:** `watson_stt`

**Models:**
- `en-US_Telephony` - Optimized for phone audio (recommended for phone channels)
- `en-US_BroadbandModel` - For high-quality audio
- `en-US_Multimedia` - For varied audio sources

**Settings:**

**smart_formatting** (boolean, default: true)
- Converts numbers, dates, times to readable format
- Example: "twenty five" → "25"

**profanity_filter** (boolean, default: false)
- Masks profanity in transcripts
- Set to true for customer-facing applications

**end_of_phrase_silence_time** (number, default: 0.8)
- Seconds of silence to detect end of phrase
- Range: 0.0 to 2.0
- Lower values = faster response, may cut off speech
- Higher values = more patient, may feel slow

**split_transcript_at_phrase_end** (boolean, default: true)
- Split transcript at phrase boundaries
- Improves conversation flow

**Authentication:**
- Method: API Key
- Required: `api_key`, `service_url`

### Google Cloud Speech-to-Text
**Provider:** `google_stt`

**Models:**
- `phone_call` - Optimized for telephony
- `default` - General purpose

**Authentication:**
- Method: Service Account JSON
- Required: `service_account_json`

### Azure Cognitive Services Speech
**Provider:** `azure_stt`

**Authentication:**
- Method: Subscription Key
- Required: `subscription_key`, `region`

## TTS Providers

### Watson Text to Speech
**Provider:** `watson_tts`

**Voices:**
- `en-US_MichaelV3Voice` - Male, US English
- `en-US_AllisonV3Voice` - Female, US English
- `en-US_EmilyV3Voice` - Female, US English
- `en-GB_CharlotteV3Voice` - Female, UK English

**Settings:**

**rate** (string, default: "0%")
- Speech rate adjustment
- Format: Percentage from "-20%" to "+20%"
- Negative = slower, Positive = faster

**pitch** (string, default: "0%")
- Voice pitch adjustment
- Format: Percentage from "-20%" to "+20%"
- Negative = lower pitch, Positive = higher pitch

**Authentication:**
- Method: API Key
- Required: `api_key`, `service_url`

### Google Cloud Text-to-Speech
**Provider:** `google_tts`

**Voices:**
- `en-US-Neural2-A` through `en-US-Neural2-J` - Various neural voices

**Authentication:**
- Method: Service Account JSON
- Required: `service_account_json`

### Azure Cognitive Services Speech
**Provider:** `azure_tts`

**Voices:**
- `en-US-JennyNeural` - Female
- `en-US-GuyNeural` - Male

**Authentication:**
- Method: Subscription Key
- Required: `subscription_key`, `region`

## Audio Configuration

### sample_rate
**Description:** Audio sampling rate in Hz

**Common Values:**
- `8000` - Telephony quality (phone calls) - **Recommended for phone channels**
- `16000` - Wideband (better quality)
- `48000` - High quality

**Recommendation:** Use 8000 for phone channels, 16000+ for others

### encoding
**Description:** Audio encoding format

**Common Values:**
- `mulaw` - Standard for telephony - **Recommended for phone**
- `linear16` - Uncompressed PCM
- `opus` - Efficient compression - **Recommended for messaging**

**Recommendation:** Use mulaw for phone, opus for messaging

### channels
**Description:** Number of audio channels

**Values:**
- `1` - Mono (standard for voice) - **Always use this**
- `2` - Stereo

**Recommendation:** Always use 1 (mono) for voice agents

## Language Support

### English (United States)
**Code:** `en-US`

**STT Models:**
- Watson: `en-US_Telephony`
- Google: `en-US`
- Azure: `en-US`

**TTS Voices:**
- Watson: `en-US_MichaelV3Voice`
- Google: `en-US-Neural2-A`
- Azure: `en-US-JennyNeural`

### Spanish (Spain)
**Code:** `es-ES`

**STT Models:**
- Watson: `es-ES_BroadbandModel`
- Google: `es-ES`
- Azure: `es-ES`

**TTS Voices:**
- Watson: `es-ES_EnriqueV3Voice`
- Google: `es-ES-Neural2-A`
- Azure: `es-ES-ElviraNeural`

## Creating Voice Configuration

### Step 1: Search ADK Documentation
Before creating, search for:
- "voice configuration YAML specification"
- "STT TTS provider configuration"
- "[provider_name] configuration"

### Step 2: Create YAML File
Create voice configuration YAML based on requirements and ADK docs.

### Step 3: Import to Orchestrate
```bash
wxo voice-config import voice_config.yaml
```

### Step 4: Verify Creation
```bash
wxo voice-config list
```

## Configuration Examples

### Phone Channel Configuration
```yaml
spec_version: v1
kind: VoiceConfiguration
name: phone-voice-config
description: Optimized for phone calls

stt_provider:
  provider: watson_stt
  model: en-US_Telephony  # Telephony-optimized
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: en-US_MichaelV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 8000  # Telephony quality
  encoding: mulaw    # Standard for phone
  channels: 1        # Mono
```

### High-Quality Messaging Configuration
```yaml
spec_version: v1
kind: VoiceConfiguration
name: messaging-voice-config
description: High quality for messaging channels

stt_provider:
  provider: watson_stt
  model: en-US_BroadbandModel  # Higher quality
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: en-US_AllisonV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 16000  # Wideband quality
  encoding: opus      # Efficient compression
  channels: 1
```

### Multi-Language Configuration (English)
```yaml
spec_version: v1
kind: VoiceConfiguration
name: voice-config-en
description: English voice configuration

stt_provider:
  provider: watson_stt
  model: en-US_Telephony
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: en-US_MichaelV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 8000
  encoding: mulaw
  channels: 1
```

### Multi-Language Configuration (Spanish)
```yaml
spec_version: v1
kind: VoiceConfiguration
name: voice-config-es
description: Spanish voice configuration

stt_provider:
  provider: watson_stt
  model: es-ES_BroadbandModel
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: es-ES_EnriqueV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 8000
  encoding: mulaw
  channels: 1
```

## Tuning Voice Configuration

### Adjusting STT Sensitivity
**Problem:** STT cuts off user speech too early

**Solution:** Increase `end_of_phrase_silence_time`
```yaml
end_of_phrase_silence_time: 1.2  # More patient
```

**Problem:** STT feels slow to respond

**Solution:** Decrease `end_of_phrase_silence_time`
```yaml
end_of_phrase_silence_time: 0.5  # Faster response
```

### Adjusting TTS Speed
**Problem:** Agent speaks too fast

**Solution:** Decrease rate
```yaml
rate: "-10%"  # 10% slower
```

**Problem:** Agent speaks too slow

**Solution:** Increase rate
```yaml
rate: "+10%"  # 10% faster
```

### Adjusting TTS Pitch
**Problem:** Voice sounds too high

**Solution:** Decrease pitch
```yaml
pitch: "-10%"  # Lower pitch
```

**Problem:** Voice sounds too low

**Solution:** Increase pitch
```yaml
pitch: "+10%"  # Higher pitch
```

## Best Practices

- Search ADK docs for latest voice config specification before creating
- Use telephony-optimized models for phone channels
- Match sample rate to channel requirements (8000 for phone)
- Test different voices to find best fit for use case
- Enable smart_formatting for better transcript readability
- Adjust end_of_phrase_silence_time based on user testing
- Keep rate and pitch at 0% initially, adjust based on feedback
- Use consistent voice configuration across related agents
- Create separate configs for different languages
- Document configuration decisions in plan.md

## Troubleshooting

### Poor STT Accuracy
**Symptoms:** Frequent misunderstandings

**Checks:**
- Verify audio quality and sample rate
- Check language model selection
- Review background noise levels

**Solutions:**
- Switch to appropriate acoustic model (telephony vs broadband)
- Enable noise reduction
- Consider custom language model for domain terms
- Adjust silence detection sensitivity

### Unnatural TTS
**Symptoms:** Robotic or awkward speech

**Checks:**
- Verify voice selection
- Check rate and pitch settings
- Review response text formatting

**Solutions:**
- Try different voices
- Adjust rate for more natural pacing
- Use conversational language in responses
- Add pauses with SSML if needed

### Audio Quality Issues
**Symptoms:** Choppy or distorted audio

**Checks:**
- Verify sample rate matches channel
- Check encoding format
- Review network connectivity

**Solutions:**
- Use appropriate sample rate (8000 for phone)
- Use correct encoding (mulaw for phone, opus for messaging)
- Test with different audio configurations
- Check for network latency issues