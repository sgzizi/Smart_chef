
# **SmartChef: AI-Powered Meal Assistant**

**SmartChef** is an intelligent recipe and health advice generator that combines personalized meal suggestions with health tips, interactive voice playback, and weather-based recommendations. It allows users to input ingredients, health goals, and city location to receive tailored recipe suggestions, nutritional insights, and more.

---

## **Features**

- **Personalized Meal Recommendations**  
  SmartChef uses AI-powered algorithms to generate recipe suggestions based on the user's ingredients, dietary preferences, and health goals (e.g., fat loss, muscle gain).

- **Weather-Based Meal Suggestions**  
  The system integrates **WeatherAPI** to fetch real-time weather data and provide meal recommendations tailored to the current weather conditions (e.g., hot meals for cold weather, refreshing dishes for hot weather).

- **Voice Playback**  
  Users can listen to their recipe recommendations and health advice via a voice assistant. The voice playback allows users to adjust the speaking speed and enjoy a personalized, hands-free experience.

- **YouTube Video Recommendations**  
  Based on the generated recipe suggestions, SmartChef recommends relevant cooking videos from YouTube, providing users with visual guidance to prepare their meals.

- **Interactive Q&A with Context Memory**  
  The AI allows users to ask follow-up questions about their health goals or recipes. The system remembers previous conversations and continues from where the last interaction left off, offering a seamless and engaging experience.

---

## **Technologies Used**

1. **Frontend:**
   - **Streamlit:** An open-source Python framework used to quickly build an interactive user interface for web applications. This framework enables users to interact with the app effortlessly.

2. **Backend:**
   - **Python:** The core language for implementing backend logic and data processing.
   - **DeepSeek API:** Provides AI-powered health and recipe suggestions based on user input.
   - **WeatherAPI:** Retrieves real-time weather data for cities to recommend weather-appropriate meals.
   - **YouTube Data API:** Fetches relevant cooking videos based on the recommended recipes.

3. **Voice Playback:**
   - **pyttsx3:** Used for generating text-to-speech audio, enabling users to listen to their health reports and recipe instructions.

---

## **How It Works**

### **1. User Input and Data Collection**

- Users enter information such as:
  - **City:** The location is used to fetch weather data.
  - **Ingredients:** The items the user currently has in their kitchen.
  - **Dietary Preferences:** The user’s preferences, such as low-carb, high-protein, or vegetarian.
  - **Health Goals:** Examples include fat loss, muscle gain, etc.

### **2. Fetch Weather Information**

- **WeatherAPI** is used to retrieve real-time weather data based on the user’s city. This information is used to influence the recipe suggestions:
  - Cold weather: Comforting meals
  - Hot weather: Refreshing and hydrating meals

### **3. AI-Powered Health and Recipe Suggestions**

- **DeepSeek API** analyzes the user’s input data and generates personalized meal recommendations.
- Nutritional insights are provided to help users understand the health benefits of the suggested meals.

### **4. Voice Playback**

- Users can click a button to have the app read out loud the entire health report and recipe instructions.
- Voice speed can be adjusted, making the experience feel like a conversation with a friend.

### **5. Video Recommendations**

- The app uses **YouTube Data API** to recommend relevant cooking videos based on the recipe suggestions, helping users visualize how to cook their meals.

### **6. Interactive Q&A with Context Memory**

- The AI-powered chat system remembers past interactions and continues conversations seamlessly. Users can ask follow-up questions about recipes, ingredients, or health tips.

---

## **Installation**

### **Requirements**

- Python 3.x
- Streamlit
- DeepSeek API Key
- YouTube API Key
- WeatherAPI Key
- pyttsx3
- emoji

### **Setup**

1. Clone the repository:
   ```bash
   git clone https://github.com/sgzizi/Smart_chef.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Smart_chef
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root and add the following:
     ```
     DEEPSEEK_API_KEY=your_deepseek_api_key
     YOUTUBE_API_KEY=your_youtube_api_key
     WEATHER_API_KEY=your_weather_api_key
     ```

### **Run the Application**

To run the application, simply execute:

```bash
streamlit run app.py
```

This will launch the app in your web browser.

---

## **Deployment**

### **Online Usage (Zero Configuration)**

- Users can access the deployed app via the following link:  
  [https://smartchef-g16-pacers.streamlit.app/](https://smartchef-g16-pacers.streamlit.app/)
- No installation or setup required. Just open the link and start using it.

### **Local Deployment (Developer Mode)**

- Developers can clone the project from **GitHub** and run it locally:
  ```bash
  git clone https://github.com/sgzizi/Smart_chef.git
  cd Smart_chef
  pip install -r requirements.txt
  streamlit run app.py
  ```

- This allows further development or customizations of the app.

---

## **Contributing**

We encourage contributions to this project! Feel free to fork the repository, submit pull requests, or suggest improvements.

---

## **License**

This project is open-source and licensed under the MIT License.
