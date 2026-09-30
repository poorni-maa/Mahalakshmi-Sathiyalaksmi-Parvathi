// ============================================================
// EDUGENIE FRONTEND JAVASCRIPT
// ============================================================


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ============================================================
// SHOW RESULT
// ============================================================

function showResult(
    elementId,
    content,
    isError = false
) {

    const element =
        document.getElementById(elementId);

    element.classList.add("visible");

    element.classList.toggle(
        "error",
        isError
    );

    element.innerHTML = content;
}


// ============================================================
// SHOW LOADING
// ============================================================

function showLoading(elementId) {

    showResult(
        elementId,
        `
        <span class="loading">
            🧠 EduGenie is thinking...
        </span>
        `
    );
}


// ============================================================
// GENERIC API REQUEST
// ============================================================

async function sendRequest(
    url,
    data
) {

    const response = await fetch(
        url,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body:
                JSON.stringify(data)
        }
    );


    let result;

    try {

        result =
            await response.json();

    } catch {

        throw new Error(
            "The server returned an invalid response."
        );
    }


    if (!response.ok) {

        throw new Error(
            result.error ||
            "Something went wrong."
        );
    }


    return result;
}


// ============================================================
// BUTTON LOADING STATE
// ============================================================

function setButtonLoading(
    button,
    loading
) {

    if (loading) {

        button.dataset.originalText =
            button.textContent;

        button.textContent =
            "Thinking...";

        button.disabled = true;

    } else {

        button.textContent =
            button.dataset.originalText ||
            "Submit";

        button.disabled = false;
    }
}


// ============================================================
// QUESTION FORM
// ============================================================

const questionForm =
    document.getElementById(
        "questionForm"
    );


questionForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const input =
            document.getElementById(
                "question"
            );


        const button =
            questionForm.querySelector(
                "button"
            );


        const question =
            input.value.trim();


        if (!question) {

            showResult(
                "questionResult",
                "Please enter a question.",
                true
            );

            return;
        }


        showLoading(
            "questionResult"
        );


        setButtonLoading(
            button,
            true
        );


        try {

            const data =
                await sendRequest(
                    "/api/ask",
                    {
                        question:
                            question
                    }
                );


            showResult(
                "questionResult",
                escapeHtml(
                    data.answer
                )
            );

        } catch (error) {

            showResult(
                "questionResult",
                escapeHtml(
                    error.message
                ),
                true
            );

        } finally {

            setButtonLoading(
                button,
                false
            );
        }
    }
);


// ============================================================
// EXPLAIN FORM
// ============================================================

const explainForm =
    document.getElementById(
        "explainForm"
    );


explainForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const input =
            document.getElementById(
                "topic"
            );


        const button =
            explainForm.querySelector(
                "button"
            );


        const topic =
            input.value.trim();


        if (!topic) {

            showResult(
                "explainResult",
                "Please enter a topic.",
                true
            );

            return;
        }


        showLoading(
            "explainResult"
        );


        setButtonLoading(
            button,
            true
        );


        try {

            const data =
                await sendRequest(
                    "/api/explain",
                    {
                        topic:
                            topic
                    }
                );


            showResult(
                "explainResult",
                escapeHtml(
                    data.explanation
                )
            );

        } catch (error) {

            showResult(
                "explainResult",
                escapeHtml(
                    error.message
                ),
                true
            );

        } finally {

            setButtonLoading(
                button,
                false
            );
        }
    }
);


// ============================================================
// SUMMARY FORM
// ============================================================

const summaryForm =
    document.getElementById(
        "summaryForm"
    );


summaryForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const input =
            document.getElementById(
                "summaryText"
            );


        const button =
            summaryForm.querySelector(
                "button"
            );


        const text =
            input.value.trim();


        if (!text) {

            showResult(
                "summaryResult",
                "Please paste some study material.",
                true
            );

            return;
        }


        showLoading(
            "summaryResult"
        );


        setButtonLoading(
            button,
            true
        );


        try {

            const data =
                await sendRequest(
                    "/api/summarize",
                    {
                        text:
                            text
                    }
                );


            showResult(
                "summaryResult",
                escapeHtml(
                    data.summary
                )
            );

        } catch (error) {

            showResult(
                "summaryResult",
                escapeHtml(
                    error.message
                ),
                true
            );

        } finally {

            setButtonLoading(
                button,
                false
            );
        }
    }
);


// ============================================================
// QUIZ FORM
// ============================================================

const quizForm =
    document.getElementById(
        "quizForm"
    );


quizForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const input =
            document.getElementById(
                "quizTopic"
            );


        const button =
            quizForm.querySelector(
                "button"
            );


        const topic =
            input.value.trim();


        if (!topic) {

            showResult(
                "quizResult",
                "Please enter a quiz topic.",
                true
            );

            return;
        }


        showLoading(
            "quizResult"
        );


        setButtonLoading(
            button,
            true
        );


        try {

            const data =
                await sendRequest(
                    "/api/quiz",
                    {
                        topic:
                            topic
                    }
                );


            renderQuiz(
                data.quiz
            );

        } catch (error) {

            showResult(
                "quizResult",
                escapeHtml(
                    error.message
                ),
                true
            );

        } finally {

            setButtonLoading(
                button,
                false
            );
        }
    }
);


// ============================================================
// QUIZ RENDERER
// ============================================================

let currentQuiz = [];


function renderQuiz(quiz) {

    currentQuiz = quiz;


    let html = `

        <div>

            <p style="margin-bottom: 18px;">
                <strong>
                    Choose one answer for each question.
                </strong>
            </p>

    `;


    quiz.forEach(
        function (item, index) {

            html += `

                <div class="quiz-question">

                    <h3>
                        ${index + 1}.
                        ${escapeHtml(
                item.question
            )}
                    </h3>

            `;


            item.options.forEach(
                function (option, optionIndex) {

                    const optionId =
                        `question_${index}_option_${optionIndex}`;


                    html += `

                        <label
                            class="quiz-option"
                            for="${optionId}"
                        >

                            <input
                                type="radio"
                                id="${optionId}"
                                name="question_${index}"
                                value="${escapeHtml(
                        option
                    )}"
                            >

                            <span>
                                ${escapeHtml(
                        option
                    )}
                            </span>

                        </label>

                    `;
                }
            );


            html += `

                </div>

            `;
        }
    );


    html += `

            <button
                type="button"
                class="quiz-submit"
                onclick="checkQuiz()"
            >
                Check Answers
            </button>


            <div id="quizScore"></div>

        </div>

    `;


    showResult(
        "quizResult",
        html
    );
}


// ============================================================
// CHECK QUIZ
// ============================================================

function checkQuiz() {

    let score = 0;


    currentQuiz.forEach(
        function (question, index) {

            const selected =
                document.querySelector(
                    `input[name="question_${index}"]:checked`
                );


            if (
                selected &&
                selected.value ===
                question.answer
            ) {

                score++;
            }
        }
    );


    const scoreElement =
        document.getElementById(
            "quizScore"
        );


    scoreElement.className =
        "quiz-score";


    scoreElement.textContent =
        `Your Score: ${score} / ${currentQuiz.length}`;
}


// ============================================================
// RECOMMENDATIONS FORM
// ============================================================

const recommendationForm =
    document.getElementById(
        "recommendationForm"
    );


recommendationForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const input =
            document.getElementById(
                "recommendationTopic"
            );


        const button =
            recommendationForm.querySelector(
                "button"
            );


        const topic =
            input.value.trim();


        if (!topic) {

            showResult(
                "recommendationResult",
                "Please enter a topic.",
                true
            );

            return;
        }


        showLoading(
            "recommendationResult"
        );


        setButtonLoading(
            button,
            true
        );


        try {

            const data =
                await sendRequest(
                    "/api/recommendations",
                    {
                        topic:
                            topic
                    }
                );


            showResult(
                "recommendationResult",
                escapeHtml(
                    data.recommendations
                )
            );

        } catch (error) {

            showResult(
                "recommendationResult",
                escapeHtml(
                    error.message
                ),
                true
            );

        } finally {

            setButtonLoading(
                button,
                false
            );
        }
    }
);