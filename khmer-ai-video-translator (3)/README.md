# Khmer AI Video Translator

## ការដំណើរការ
1. Python 3.10+ និង FFmpeg ត្រូវបានដំឡើង។
2. រត់ `pip install -r requirements.txt`
3. ចម្លង `.streamlit/secrets.toml.example` ទៅ `.streamlit/secrets.toml` ហើយបំពេញ API keys។
4. រត់ `streamlit run app.py`

## Deploy
ប្រើ Streamlit Community Cloud ហើយដាក់ secrets ទាំង 3 ក្នុង App settings > Secrets:
- OPENAI_API_KEY
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION

កុំបង្ហោះ API keys ឬ `secrets.toml` ពិតទៅ GitHub។

## ចំណុចដែលកំណែ MVP នេះមាន
- Upload វីដេអូ
- Whisper ស្គាល់សំឡេង និង timestamp
- AI បកប្រែទៅខ្មែរ
- Azure TTS បង្កើតសំឡេងខ្មែរ
- FFmpeg បង្កើត MP4 និង Subtitle SRT

## ដែនកំណត់សំខាន់
- កំណែនេះជ្រើសសំឡេងប្រុស ឬស្រីសម្រាប់វីដេអូទាំងមូល។ វាមិនទាន់សម្គាល់អ្នកនិយាយច្រើននាក់ដោយស្វ័យប្រវត្តិទេ។
- ការបកប្រែ និង TTS អាចត្រូវការកែសម្រួល timing។
- សាកល្បងជាមួយវីដេអូខ្លីជាមុន។
- ប្រើតែវីដេអូដែលអ្នកមានសិទ្ធិប្រើប្រាស់។

សំឡេងខ្មែរ៖ `km-KH-PisethNeural` (ប្រុស), `km-KH-SreymomNeural` (ស្រី)
