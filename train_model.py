# health_tracker_app/train_model.py

from health_model import EnhancedHealthModel
import os

# Define the path to your training data CSV file
# Make sure health_data.csv is in the same directory as train_model.py
DATA_PATH = 'health_data.csv'
MODEL_PATH = 'enhanced_health_model.pkl'

def main():
    """
    Main function to train and save the EnhancedHealthModel.
    """
    print("Starting model training process...")
    
    # Create an instance of the EnhancedHealthModel
    model = EnhancedHealthModel()
    
    try:
        # Train the model using the specified data path
        model.train(DATA_PATH)
        
        # Save the trained model to a pickle file
        model.save(MODEL_PATH)
        
        print(f"Model successfully trained and saved to {MODEL_PATH}")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure '{DATA_PATH}' exists and is in the same directory as train_model.py.")
    except Exception as e:
        print(f"An unexpected error occurred during training: {e}")

if __name__ == "__main__":
    main()

