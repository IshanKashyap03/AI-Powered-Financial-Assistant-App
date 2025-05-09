export const uploadFile = async (formData) => { 
    const res = await fetch("/api/v1/upload", {
        method: "POST",
        body: formData
    });
    if (!res.ok) throw new Error('Failed to upload file');
    return await res.json();
}