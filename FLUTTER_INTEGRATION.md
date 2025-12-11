# Flutter/Dart Web Integration Guide

## API Endpoint
```
https://web-production-4f6b5.up.railway.app
```

## Flutter/Dart Code Example

### Using http package

```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TranscriptionService {
  static const String baseUrl = 'https://web-production-4f6b5.up.railway.app';
  
  Future<Map<String, dynamic>> transcribeAudio(File audioFile, {String? language}) async {
    try {
      // Create multipart request
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );
      
      // Add file
      request.files.add(
        await http.MultipartFile.fromPath('file', audioFile.path),
      );
      
      // Add language parameter if provided
      if (language != null) {
        request.fields['language'] = language;
      }
      
      // Send request
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to transcribe: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error transcribing audio: $e');
    }
  }
  
  Future<Map<String, dynamic>> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Health check failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error checking health: $e');
    }
  }
}
```

### Complete Flutter Widget Example

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AudioTranscriberPage extends StatefulWidget {
  @override
  _AudioTranscriberPageState createState() => _AudioTranscriberPageState();
}

class _AudioTranscriberPageState extends State<AudioTranscriberPage> {
  File? _audioFile;
  Map<String, dynamic>? _result;
  bool _loading = false;
  String? _error;
  
  static const String apiUrl = 'https://web-production-4f6b5.up.railway.app';

  Future<void> _pickAudioFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
      );

      if (result != null) {
        setState(() {
          _audioFile = File(result.files.single.path!);
          _result = null;
          _error = null;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error picking file: $e';
      });
    }
  }

  Future<void> _transcribeAudio() async {
    if (_audioFile == null) {
      setState(() {
        _error = 'Please select an audio file first';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiUrl/transcribe'),
      );

      request.files.add(
        await http.MultipartFile.fromPath('file', _audioFile!.path),
      );

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _result = json.decode(response.body);
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Error: ${response.statusCode}\n${response.body}';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Audio Transcription'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: _pickAudioFile,
              child: Text('Select Audio File'),
            ),
            SizedBox(height: 16),
            if (_audioFile != null)
              Text('Selected: ${_audioFile!.path.split('/').last}'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loading ? null : _transcribeAudio,
              child: _loading
                  ? CircularProgressIndicator()
                  : Text('Transcribe'),
            ),
            if (_error != null)
              Padding(
                padding: EdgeInsets.all(8.0),
                child: Text(
                  _error!,
                  style: TextStyle(color: Colors.red),
                ),
              ),
            if (_result != null) ...[
              SizedBox(height: 16),
              Text(
                'Summary',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(_result!['summary'] ?? 'No summary'),
              SizedBox(height: 16),
              Text(
                'Action Items',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              if (_result!['action_items'] != null)
                ...(_result!['action_items'] as List).map((item) => Padding(
                      padding: EdgeInsets.symmetric(vertical: 4.0),
                      child: Text(
                        '• ${item['assignee']}: ${item['description']}',
                      ),
                    )),
            ],
          ],
        ),
      ),
    );
  }
}
```

### Using dio package (Alternative)

```dart
import 'package:dio/dio.dart';
import 'dart:io';

class TranscriptionService {
  final Dio dio = Dio();
  static const String baseUrl = 'https://web-production-4f6b5.up.railway.app';
  
  Future<Map<String, dynamic>> transcribeAudio(File audioFile, {String? language}) async {
    try {
      String fileName = audioFile.path.split('/').last;
      
      FormData formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          audioFile.path,
          filename: fileName,
        ),
        if (language != null) 'language': language,
      });
      
      Response response = await dio.post(
        '$baseUrl/transcribe',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to transcribe: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error transcribing audio: $e');
    }
  }
}
```

## Response Structure

```dart
{
  "success": true,
  "transcription": "Full transcription text...",
  "summary": "Call participants: Anthony, Fania. Topics discussed:...",
  "action_items": [
    {
      "assignee": "Anthony",
      "description": "process that from here",
      "speaker": "Anthony",
      "timestamp": 166.6,
      "date": "three to four days",
      "time": null
    }
  ],
  "language_detected": "en",
  "transcription_with_speakers": [...],
  "segments": [...],
  "metadata": {...}
}
```

## Handling Errors

### 502 Bad Gateway
This means the server is down or not responding. Check:
1. Railway deployment status
2. Server logs in Railway dashboard
3. Health endpoint: `GET /health`

### CORS Errors
If you still get CORS errors:
1. Make sure Railway has redeployed with latest code
2. Check browser console for specific error
3. Verify server is returning CORS headers

### Network Errors
```dart
try {
  var result = await transcriptionService.transcribeAudio(audioFile);
  // Handle success
} on SocketException {
  // No internet connection
} on HttpException {
  // HTTP error (502, 500, etc.)
} catch (e) {
  // Other errors
}
```

## Testing

Test the health endpoint first:

```dart
Future<void> testHealth() async {
  try {
    final response = await http.get(
      Uri.parse('https://web-production-4f6b5.up.railway.app/health'),
    );
    print('Health: ${response.body}');
  } catch (e) {
    print('Error: $e');
  }
}
```

## pubspec.yaml Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  file_picker: ^6.1.1
  # OR use dio instead of http:
  # dio: ^5.4.0
```

## Important Notes

1. **502 Bad Gateway** - Server is down or crashed. Check Railway logs
2. **CORS** - Should be fixed after Railway redeploys
3. **File Upload** - Use `MultipartFile.fromPath` or `MultipartFile.fromFile`
4. **Error Handling** - Always wrap API calls in try-catch
5. **Loading States** - Show loading indicator during transcription

## Troubleshooting

1. **502 Error**: Server needs to be restarted/redeployed on Railway
2. **CORS Error**: Wait for Railway redeployment, then clear browser cache
3. **File Upload Fails**: Check file size limits and format
4. **Timeout**: Large files may take time - increase timeout if needed

