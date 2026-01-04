# NJMTech Upload Blob API

This is a simple FastAPI application to upload files to Vercel Blob storage.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**

    Create a `.env.local` file in the root of the project and add your Vercel Blob read-write token:

    ```
    BLOB_READ_WRITE_TOKEN="YOUR_BLOB_READ_WRITE_TOKEN"
    ```

    Replace `"YOUR_BLOB_READ_WRITE_TOKEN"` with your actual token.

3.  **Run the application:**

    ```bash
    uvicorn api.main:app --reload
    ```

    The application will be running at `http://127.0.0.1:8000`.

## API Endpoint

### Upload File

*   **URL:** `/api/upload`
*   **Method:** `POST`
*   **Form Data:** `file` (the file to upload)

**Example using `curl`:**

```bash
curl -X POST -F "file=@/path/to/your/file.txt" http://127.0.0.1:8000/api/upload
```
