document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!"); 

    const searchButton = document.querySelector(".search-btn");
    const closeButton = document.querySelector(".close-btn");
    const searchPopup = document.getElementById("searchPopup");
    const searchBox = document.getElementById("searchBox");
    const searchMessage = document.getElementById("searchMessage");
    const supportButton = document.getElementById("supportButton");

    const searchedResultContainer = document.querySelector(".searched-result");
    const relevantResultsContainer = document.querySelector(".relevant-results-grid");
    const searchedResultSection = document.getElementById("searchedResultSection"); 

    
    searchedResultContainer.style.display = "none";
    relevantResultsContainer.style.display = "none";

    searchButton.addEventListener("click", function () {
        console.log("Search button clicked!");
        searchPopup.style.display = "flex";
        searchBox.focus();
    });

    closeButton.addEventListener("click", function () {
        console.log("Close button clicked!");
        searchPopup.style.display = "none";
    });

    searchPopup.addEventListener("click", function (event) {
        if (event.target === searchPopup) {
            console.log("Closing search popup!");
            searchPopup.style.display = "none";
        }
    });

    searchBox.addEventListener("input", async function () {
        const query = searchBox.value.trim();
        console.log("User is typing:", query);
    
        if (query === "") {
            searchMessage.innerText = "Start typing to discover new opportunities...";
            searchedResultContainer.style.display = "none";
            supportButton.style.display = "none";
            return;
        }
    
        try {
            const response = await fetch(`/search_professions?q=${encodeURIComponent(query)}`);
            const resultData = await response.json();
    
            console.log("Search results:", resultData);
    
            if (resultData.professions.length > 0) {
                searchMessage.innerHTML = ""; 
                resultData.professions.forEach(prof => {
                    const resultItem = document.createElement("div");
                    resultItem.classList.add("search-result");
                    resultItem.setAttribute("data-id", prof.id);
                    resultItem.innerText = prof.name;
                    searchMessage.appendChild(resultItem); 
                });
                supportButton.style.display = "none";
            } else {
                searchMessage.innerText = "No results found.";
                supportButton.style.display = "block";
            }
        } catch (error) {
            console.error("Error fetching search results:", error);
            searchMessage.innerText = "An error occurred. Please try again.";
            supportButton.style.display = "none";
        }
    });

    searchMessage.addEventListener("click", async function (event) {
        const target = event.target;

        if (target.classList.contains("search-result")) {
            const professionId = target.getAttribute("data-id");
            console.log("User clicked on profession ID:", professionId);

            try {
                // Fetch the searched profession details
                const response = await fetch(`/get_profession?id=${encodeURIComponent(professionId)}`);
                const profession = await response.json();

                console.log("Fetched profession details:", profession);

                if (profession.error) {
                    console.error("Error: ", profession.error);
                    return;
                }

                // Display the searched profession result 
                searchedResultContainer.querySelector(".img2").src = profession.image ? `/image/${professionId}` : "default-placeholder.png";
                searchedResultContainer.querySelector(".text2").innerText = profession.name;
                searchedResultContainer.querySelector(".hidden-para2").innerText = profession.description;

                // Set the data-id attribute for the "Read more" button
                const readMoreButton = searchedResultContainer.querySelector(".hidden-btn2");
                readMoreButton.setAttribute("data-id", professionId); 

                searchedResultContainer.style.display = "block"; 

                // Fetch relevant professions
                const relevantResponse = await fetch(`/get_relevant_data?profession_id=${encodeURIComponent(professionId)}`);
                const relevantData = await relevantResponse.json();

                console.log("Fetched relevant professions:", relevantData);

                if (relevantData.length > 0) {
                    
                    if (!relevantResultsContainer) {
                        console.error("Error: relevantResultsContainer not found in the HTML!");
                        return;
                    }

                    
                    relevantResultsContainer.innerHTML = "";

                    // Apply flexbox to display relevant results side by side
                    relevantResultsContainer.style.display = "flex";
                    relevantResultsContainer.style.flexWrap = "wrap";
                    relevantResultsContainer.style.justifyContent = "center"; 
                    relevantResultsContainer.style.gap = "15px"; 

                    // Display relevant professions, each in its own purple-container2
                    relevantData.forEach(relevantProfession => {
                        console.log("Appending relevant profession:", relevantProfession);

                        const relevantProfessionContainer = document.createElement("div");
                        relevantProfessionContainer.classList.add("purple-container2");

                        relevantProfessionContainer.innerHTML = `
                            <img class="img img2" src="${relevantProfession.image ? `/image/${relevantProfession.id}` : 'default-placeholder.png'}" alt="Image">
                            <span class="text text2">${relevantProfession.name}</span>
                            <p class="hidden-para hidden-para2">${relevantProfession.description}</p>
                            <button class="hidden-btn hidden-btn2" data-id="${relevantProfession.id}" onclick="redirectToDetails(event)">Read more</button>
                        `;

                        relevantResultsContainer.appendChild(relevantProfessionContainer);
                    });

                    relevantResultsContainer.style.display = ""; 
                } else {
                    relevantResultsContainer.innerHTML = "<p>No relevant data found.</p>";
                    relevantResultsContainer.style.display = "block"; 
                }

                // Auto-scroll to the searched result section
                searchedResultSection.scrollIntoView({ behavior: "smooth", block: "start" }); 
            } catch (error) {
                console.error("Error fetching profession details:", error);
            }

            searchPopup.style.display = "none";
        }
    });

    // Redirect to support.html when Support Button is clicked
    supportButton.addEventListener("click", function () {
        console.log("Redirecting to support page...");
        window.location.href = "/support";
    });

    // Function to redirect to details page
    function redirectToDetails(event) {
        event.preventDefault();
        const professionId = event.target.getAttribute("data-id");
        if (professionId) {
            window.location.href = `/details?id=${professionId}`;
        }
    }

    // Add event listener to "Read more" buttons in searched result container
    searchedResultContainer.addEventListener("click", function (event) {
        const target = event.target;

        if (target.classList.contains("hidden-btn2")) {
            const professionId = target.getAttribute("data-id");
            console.log("User clicked on profession ID in searched result:", professionId);
            redirectToDetails(event);
        }
    });
});
