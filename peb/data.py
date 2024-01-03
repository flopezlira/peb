(
    START,
    GOAL,
    PERSONA,
    TASK,
    WHOM,
    HOW,
    FORMAT,
    CONSTRAINTS,
    TOOL,
    QUALITY,
    OPENAI,
    PAYMENT,
    SKIP,
) = range(13)

state_code = {
    "start": START,
    "goal": GOAL,
    "persona": PERSONA,
    "task": TASK,
    "whom": WHOM,
    "how": HOW,
    "format": FORMAT,
    "constraints": CONSTRAINTS,
    "tool": TOOL,
    "quality": QUALITY,
    "openai": OPENAI,
    "payment": PAYMENT,
    "skip": SKIP,
}

final_message = {
    "goal": "My goal is:",
    "persona": "Assume you are:",
    "task": "Your task is to:",
    "how": "To do the task you have to consider:",
    "whom": "The audience is:",
    "format": "The output format is:",
    "constraints": "Consider the following constraints and assumptions:",
    "tool": "Use the following tools:",
    "quality": "To assure quality, you have to:",
}

suggestions = {
    "how": '"Add to the prompt your suggestions for the best way, steps, strategy or approach to do the task.',
    "format": "Add to the prompt the best output format for the prompt.",
    "constraints": 'Add to the prompt your suggestions regarding assumptions, restrictions or constraints"',
    "tool": "Add to the prompt your suggestions of the best conceptual tools for the task",
    "quality": "Add to the prompt your suggestions regarding the best way to assure quality in the prompt",
}

state_examples = {
    START: [
        "None",
    ],
    GOAL: [
        "Learn Excel",
        "Understand Bayes theorem",
        "Achieve my goals in life",
        "Asses my business idea",
        "Lose weight",
        "Learn Python",
        "Have a great vacation at Rome",
        "Write a book",
    ],
    PERSONA: [
        #       "Be formal/casual/technical",
        "Expert in Excel with a technical style",
        "Math teacher with a formal style",
        "Coach with a casual style",
        "Steve Jobs",
        "Shakespeare",
        "Nutritionist",
        "SEO expert",
        "Movie critic in a humours style",
        "Math tutor with a simple language",
        "Python expert",
        "Customer service representative with a kind style",
        "Communications specialist",
        "Travel agent with a professional style",
        "Writing assistant",
    ],
    TASK: [
        "Write the first chapter of a book",
        "Assemble a course syllabus",
        "Answer this email",
        "Write a blog post",
        "Write an email",
        "Outline a diet plan",
        "Solve a problem in Excel",
        "Teach basics of Python",
        "Help me plan a vacation at Rome",
        "Correct my text",
        "Write a poem",
        "Answer a query",
        "Summarize a document",
        "Write a blog post",
        "Create a business plan",
        "Respond an email",
        "Summarize my inbox provided between triple quotes",
    ],
    HOW: [
        "Use a step-by-step approach",
        "Use this as a context: " "Use the following examples: 1+2=3",
        "Use the following inputs delimited by <> to answer questions",
        "Answer with citations to provided sources",
        "Use the following categories to classify the information: Good, Bad, Indifferent",
        "Use this categories: 'Great = positive', 'Not working = negative', 'Helpful = positive'",
        "Summarize the book/article/document by summarizing each section which I will provide to you",
        "Make a Quick summary",
    ],
    WHOM: [
        "For a person with no previous experience",
        "For busy professionals",
        "For absolute beginners",
        "For a 5 year old children",
        "For experts",
        "For a lawyer",
        "For a person with no technical background",
        "For a marketing specialist",
    ],
    FORMAT: [
        "Text",
        "Table",
        "List",
        "Summary",
        "Code snippet",
        "Plain text",
        "Rich text",
        "Gantt chart",
        "Word cloud",
        "Emoji",
        "Bullet points",
        "json",
        "CSV",
        "HTML",
        "XML",
        "Markdown",
    ],
    CONSTRAINTS: [
        "Maximum 500 words",
        "The course duration should be 3 weeks",
        "Summarize in 3 paragraphs",
        "Minimize the use of jargon",
        "Short sentence",
        "500 words",
        "Use scientific sources",
        "Avoid sensitive subjects",
        "Include the phrase x",
        "include the words abc",
        "add pop culture references",
        "include terminology from x",
    ],
    TOOL: [
        "SWOT analysis",
        "Business model canvas",
        "Ben Franklin",
        "Six hats of Bono",
        "Pareto principle",
        "Five forces of Porter",
        "Niche vision",
        "Brainstorming",
        "Constructivism /Cognitivism / Behaviorism",
        "Decision matrix",
        "Business/Lean model canvas",
        "Design thinking",
        "Persona analysis",
        "Agile framework" "OKRs",
    ],
    QUALITY: [
        "Work out your own (ChatGPT) solution before coming to a conclusion",
        "Use instructional design best practices",
        "Make sure you don't miss anything from previous steps",
        "Don't miss important context",
        "Think step-by-step",
        "Conduct an In-depth analysis",
        "Provide feedback based on clarity, completeness, and effectiveness",
        "Let's iterate on this response. Please provide an initial answer, and based on that, suggest an improved "
        "version that better matches our intended tone and purpose",
        "Feel free to adjust the phrasing, context, or details for a more accurate outcome.",
    ],
    OPENAI: ["Your promtp will be enhanced when you press 'Perfect my prompt'"],
    PAYMENT: ["Pay through Stripe"],
}

state_message = {
    START: [
        "🤖️ Welcome!",
        "\n- I will help you create a great prompt for ChatGPT!",
        "\n- I will ask you for the information interactively. ",
        "\n- There are 9 steps. The first 3 steps are mandatory",
        "\n- At the end, I will show you a summary of your answers",
        "and the option to enhance your prompt if you don't want to change anything",
        "" "\n- Once your prompt is enhanced,",
        "all you have to do is to copy it and paste it in ChatGPT",
        "\n- You can use it as it is free of charge",
        "or you can buy me a coffee or help me pay the server",
        "This will be done through our partner Stripe\n",
        '- Click on "Start again" anytime to start all over\n',
        "- ** Don't enter any personal information**\n",
    ],
    GOAL: [
        "1️⃣️",
        "Problem or Purpose",
        "State what you want to achieve or the problem you want to solve",
        "The goal is the ultimate reason why you are writing the prompt",
        "IT represents your long-term vision",
        "The goal can be divided into sub-goals or tasks, which you will define later",
    ],
    PERSONA: [
        "2️⃣️",
        "Persona & Style",
        "Ask ChatGPT to adopt a persona or a role",
        "Select the persona, role or identity you want ChatGPT to adopt",
        "Also, you can select a style of communication that you want ChatGPT to use",
    ],
    TASK: [
        "3️⃣️",
        "The What",
        "Task definition",
        "What do you want ChatGPT to do?",
        "You can divide the goal into tasks",
    ],
    HOW: [
        "4️⃣️",
        "How should ChatGPT do the task?",
    ],
    WHOM: ["5⃣️", "Provide context about the intended audience. Who is it for?"],
    FORMAT: [
        "6⃣️️",
        "Format",
        "Select the output format for your prompt. You can choose more than one",
    ],
    CONSTRAINTS: [
        "7️⃣️",
        "Constraints",
        "Enter any assumptions, restrictions or constraints that ChatGPT should follow"
        "Think of anything that ChatGPT should consider or that should not do",
    ],
    TOOL: [
        "8️⃣️",
        "Tools",
        "List a tool, model or framework that ChatGPT should use for the task",
    ],
    QUALITY: [
        "9️⃣️",
        "Quality",
        "Decide on how to assure quality in your prompt",
    ],
    OPENAI: ["Connect with OpenAI"],
    PAYMENT: ["If you like my work, you can buy me a coffee"],
}
