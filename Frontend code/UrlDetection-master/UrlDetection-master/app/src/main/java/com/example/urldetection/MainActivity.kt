package com.example.urldetection

import android.os.Bundle
import android.view.View
import android.widget.EditText
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import android.text.Editable
import android.text.TextWatcher
import android.widget.TextView
import android.widget.Toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.IOException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

class MainActivity : ComponentActivity() {

    private lateinit var url_input : EditText
    private lateinit var textView : TextView
    private var url : String = ""
    private var urlLabel : String = ""
    private var apiKey = ApiKeys.API_KEY

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)


        url_input = findViewById(R.id.textUrl)
        textView = findViewById(R.id.textView2)

        url_input.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable) {
                if (s.toString().isEmpty()) {
                    textView.visibility = View.VISIBLE
                } else {
                    textView.visibility = View.INVISIBLE
                }
            }
            override fun beforeTextChanged(s: CharSequence, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence, start: Int, before: Int, count: Int) {}
        })

        val client = OkHttpClient()
        val request = Request.Builder().url("http://172.188.50.229:5000/").build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Server down", Toast.LENGTH_SHORT).show()
                    println("Error connecting to the server")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")

                    val responseBody = response.body?.string()
                    runOnUiThread {
                        if (responseBody == "This is the Flask server!") {
                            Toast.makeText(this@MainActivity, "Server is UP !!", Toast.LENGTH_SHORT).show()
                            println("Connected to the server successfully")
                        } else {
                            Toast.makeText(this@MainActivity, "Unexpected response from the server", Toast.LENGTH_SHORT).show()
                            println("Unexpected response from the server")
                        }
                    }
                }
            }
        })
    }

    fun buttonClick(view: View?){
        url = url_input.text.toString()
        println(url)

        val client = OkHttpClient()

        val jsonUrl = "{\"url\": \"$url\"}"
        val mediaType = "application/json; charset=utf-8".toMediaType()
        val requestBody = jsonUrl.toRequestBody(mediaType)

        val postRequest = Request.Builder()
            .url("http://172.188.50.229:5000/get-url-from-frontend")
            .header("astroapi", apiKey)
            .post(requestBody)
            .build()

        client.newCall(postRequest).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Server down", Toast.LENGTH_SHORT).show()
                    println("Error connecting to the server")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
//                    if (!response.isSuccessful) throw IOException("Unexpected code $response")

                    runOnUiThread {
                        when (response.code) {
                            200 -> {
                                Toast.makeText(this@MainActivity, "Url Received. Scanning.....", Toast.LENGTH_LONG).show()
                                println("URL received by the server")
                            }
                            400 -> {
                                Toast.makeText(this@MainActivity, "Invalid Url!", Toast.LENGTH_SHORT).show()
                                println("Invalid Url!")
                            }
                            else -> {
                                Toast.makeText(this@MainActivity, "Oops! Something went wrong!", Toast.LENGTH_SHORT).show()
                                println("Oops! Something went wrong!")
                            }
                        }

                        if (response.code == 200) {
                            val getRequest = Request.Builder()
                                .url("http://172.188.50.229:5000/check-url-label")
                                .header("astroapi", apiKey)
                                .get()
                                .build()

                            val toast = Toast.makeText(this@MainActivity, "Scanning.....", Toast.LENGTH_LONG)
                            toast.show()

                            GlobalScope.launch(Dispatchers.IO) {
                                var respondStatus: Int
                                do {
                                    respondStatus = suspendCancellableCoroutine<Int> { continuation ->
                                        val request = Request.Builder()
                                            .url("http://172.188.50.229:5000/check-url-label")
                                            .header("astroapi", apiKey)
                                            .get()
                                            .build()

                                        client.newCall(request).enqueue(object : Callback {
                                            override fun onFailure(call: Call, e: IOException) {
                                                runOnUiThread {
                                                    Toast.makeText(this@MainActivity, "Server down", Toast.LENGTH_SHORT).show()
                                                    println("Error connecting to the server")
                                                }
                                                continuation.resumeWith(Result.success(200))
                                            }

                                            override fun onResponse(call: Call, response: Response) {
                                                response.use {
                                                    if (!response.isSuccessful) throw IOException("Unexpected code $response")

                                                    val responseBody = response.body?.string().toString()
                                                    toast.cancel()

                                                    runOnUiThread {
                                                        when (response.code) {
                                                            200 -> {
                                                                urlLabel = responseBody
                                                                if (urlLabel == "benign") {
                                                                    Toast.makeText(this@MainActivity, "Type: $urlLabel\n(Legitimate Website)", Toast.LENGTH_SHORT).show()
                                                                    println("This url is $urlLabel")
                                                                }
                                                                else {
                                                                    Toast.makeText(this@MainActivity, "Type: $urlLabel\n(Unsafe Website)", Toast.LENGTH_SHORT).show()
                                                                    println("This url is $urlLabel")
                                                                }
                                                            }
                                                            400 -> {
                                                                Toast.makeText(this@MainActivity, "show", Toast.LENGTH_SHORT).show()
                                                                println(responseBody)
                                                            }
                                                            else -> {
                                                                Toast.makeText(this@MainActivity, "Oops! Something went wrong!", Toast.LENGTH_SHORT).show()
                                                                println("Oops! Something went wrong!")
                                                            }
                                                        }
                                                    }
                                                    continuation.resumeWith(Result.success(response.code))
                                                }
                                            }
                                        })
                                    }
                                } while (respondStatus != 200)
                            }
                        }
                    }
                }
            }
        })
    }
}
