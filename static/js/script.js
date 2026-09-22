function analyzeResume() {

    const fileInput = document.getElementById("resumeFile");

    if (fileInput.files.length === 0) {
        alert("Please upload your resume first.");
        return;
    }

    const file = fileInput.files[0];

    const allowedExtensions = ["pdf", "doc", "docx"];

    const fileExtension = file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        alert("Please upload a PDF, DOC, or DOCX file.");
        return;
    }

    alert(
        "Resume selected successfully!\n\n" +
        "File: " + file.name
    );
}


document
    .getElementById("resumeFile")
    .addEventListener("change", function () {

        if (this.files.length > 0) {

            document.getElementById("fileName").textContent =
                "Selected file: " + this.files[0].name;

        }

    });