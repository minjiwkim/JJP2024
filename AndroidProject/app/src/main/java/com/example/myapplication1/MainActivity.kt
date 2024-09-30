package com.example.myapplication1

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.arthenica.ffmpegkit.FFmpegKit
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.ResponseBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.http.*
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var previewView: PreviewView
    private lateinit var imageCapture: ImageCapture
    private val frameCaptureInterval: Long = 1000 // 프레임 캡처 주기 (1초)
    private val outputFramePath: String
        get() = "${getFilesDir().absolutePath}/frames/frame_%03d.jpg" // 내부 저장소 경로
    private val handler = Handler()
    private var frameCount = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewView = findViewById(R.id.previewView)

        // 카메라 권한 요청
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            // Preview 설정
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            // 이미지 캡처 설정
            imageCapture = ImageCapture.Builder().build()

            // 카메라 선택
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider.unbindAll() // 이전 바인딩 해제
                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture)
                startFrameCapture() // 프레임 자동 캡처 시작
            } catch (exc: Exception) {
                Log.e("CameraX", "Binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun startFrameCapture() {
        handler.postDelayed(object : Runnable {
            override fun run() {
                captureImage()
                handler.postDelayed(this, frameCaptureInterval) // 다시 호출
            }
        }, frameCaptureInterval)
    }

    private fun captureImage() {
        val framesDir = File("${getFilesDir().absolutePath}/frames")
        if (!framesDir.exists()) {
            framesDir.mkdirs() // 디렉토리가 없으면 생성
        }

        val photoFile = File(framesDir, String.format("frame_%03d.jpg", frameCount++)) // 파일 이름 생성
        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        imageCapture.takePicture(outputOptions, ContextCompat.getMainExecutor(this), object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                Log.d("CameraX", "Image saved successfully: ${photoFile.absolutePath}")
                uploadImage(photoFile) // 이미지 업로드 호출
            }

            override fun onError(exception: ImageCaptureException) {
                Log.e("CameraX", "Error saving image: ${exception.message}")
            }
        })
    }

    // Retrofit 인터페이스 설정
    interface ApiService {
        @Multipart
        @POST("/upload/image")
        fun uploadImage(@Part image: MultipartBody.Part): Call<ResponseBody>
    }

    // Retrofit 인스턴스 생성
    private val retrofit: Retrofit by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .build()

        Retrofit.Builder()
            .baseUrl("http://10.101.7.159:8000/")  // 서버 주소
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    private val service: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }

    // JPG 파일을 전송하는 함수
    private fun uploadImage(imageFile: File) {
        val requestFile = imageFile.asRequestBody("image/jpeg".toMediaType())
        val body = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)

        val call = service.uploadImage(body)
        call.enqueue(object : Callback<ResponseBody> {
            override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                if (response.isSuccessful) {
                    val responseBody = response.body()?.string() // 응답 본문을 문자열로 변환
                    Log.d("Upload", "Image uploaded successfully! Response: $responseBody")

                    // JSON 응답을 파싱하는 로직 추가
                    try {
                        val jsonObject = JSONObject(responseBody)
                        val objectsArray = jsonObject.getJSONArray("objects")

                        // 탐지된 객체를 로그에 출력
                        for (i in 0 until objectsArray.length()) {
                            val detectedObject = objectsArray.getJSONObject(i)
                            val objectClass = detectedObject.getString("class")
                            val confidence = detectedObject.getDouble("confidence")
                            val bbox = detectedObject.getJSONArray("bbox")

                            Log.d("Detected Object", "Class: $objectClass, Confidence: $confidence, BBox: $bbox")
                        }
                    } catch (e: Exception) {
                        Log.e("Upload", "Error parsing JSON response: ${e.message}")
                    }
                } else {
                    Log.e("Upload", "Upload failed with code: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                Log.e("Upload", "Error: ${t.message}")
            }
        })
    }

    // Permissions check
    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA)
    }
}