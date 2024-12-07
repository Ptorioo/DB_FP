// Mock data for articles and comments
let articles = [
    { id: 1, title: "First Article", author: "Alice", created_time: "2024-12-01", content: "This is the first article.", comments: [] },
    { id: 2, title: "Second Article", author: "Bob", created_time: "2024-12-02", content: "This is the second article.", comments: [] }
  ];
  
  let currentPage = 0;
  const PAGE_SIZE = 1; // Number of articles per page
  
  // Elements
  const articlesList = document.getElementById("articles");
  const articleDetailSection = document.getElementById("article-detail");
  const articleListSection = document.getElementById("article-list");
  const articleTitle = document.getElementById("article-title");
  const articleMeta = document.getElementById("article-meta");
  const articleContent = document.getElementById("article-content");
  const commentsList = document.getElementById("comments");
  const commentInput = document.getElementById("comment-input");
  
  // Pagination
  document.getElementById("prev-btn").addEventListener("click", () => changePage(-1));
  document.getElementById("next-btn").addEventListener("click", () => changePage(1));
  
  function changePage(direction) {
    const totalPages = Math.ceil(articles.length / PAGE_SIZE);
    currentPage = Math.max(0, Math.min(currentPage + direction, totalPages - 1));
    renderArticles();
  }
  
  // Render articles list
  function renderArticles() {
    articlesList.innerHTML = "";
    const start = currentPage * PAGE_SIZE;
    const end = start + PAGE_SIZE;
  
    articles.slice(start, end).forEach((article, index) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <h3>${article.title}</h3>
        <p>by ${article.author} on ${article.created_time}</p>
        <button onclick="viewArticle(${article.id})">View</button>
      `;
      articlesList.appendChild(li);
    });
  }
  
  // View a single article
  function viewArticle(articleId) {
    const article = articles.find(a => a.id === articleId);
    if (!article) return;
  
    articleListSection.classList.add("hidden");
    articleDetailSection.classList.remove("hidden");
  
    articleTitle.textContent = article.title;
    articleMeta.textContent = `by ${article.author} on ${article.created_time}`;
    articleContent.textContent = article.content;
  
    renderComments(article);
  }
  
  // Render comments
  function renderComments(article) {
    commentsList.innerHTML = "";
    article.comments.forEach((comment, index) => {
      const li = document.createElement("li");
      li.textContent = `${comment.author}: ${comment.content}`;
      commentsList.appendChild(li);
    });
  
    document.getElementById("submit-comment-btn").onclick = () => {
      const content = commentInput.value.trim();
      if (content) {
        article.comments.push({ author: "CurrentUser", content });
        renderComments(article);
        commentInput.value = "";
      }
    };
  }
  
  // Back to articles list
  document.getElementById("back-btn").addEventListener("click", () => {
    articleDetailSection.classList.add("hidden");
    articleListSection.classList.remove("hidden");
  });
  
  // Initial render
  renderArticles();
  