
        // ajax like post
        let btn_like = document.querySelector("a.like");
        let like_numbers = document.getElementById("like-numbers");
        let like_word = document.getElementById("like-word");
        let like_body = document.getElementById("like-body");
        let like_container = document.getElementById("like-container");
        btn_like.addEventListener("click", function (e) {
            e.preventDefault();
            var fd = new FormData();
            fd.append("id", btn_like.getAttribute("data-id"));
            // fd.append("action", btn_like.getAttribute("data-action"));
            let activate;
            if (btn_like.classList.contains("active")) {
                activate = "dislike";
            } else {
                activate = "like";
            }
            fd.append("action", activate);
            fd.append("csrfmiddlewaretoken", "{{csrf_token}}");
            axios.post("/posts/like/", fd)
                .then((res) => {
                    btn_like.classList.toggle("active");
                    if (activate == "like") {
                        like_numbers.innerHTML = parseInt(like_numbers.innerHTML) + 1
                        if (parseInt(like_numbers.innerHTML) >= 2) {
                            like_word.innerHTML = "Likes";
                        }
                    } else {
                        like_numbers.innerHTML = parseInt(like_numbers.innerHTML) - 1
                        if (parseInt(like_numbers.innerHTML) == 1) {
                            like_word.innerHTML = "Like";
                        }
                        // else if(parseInt(like_numbers.innerHTML) == 0){
                        //     like_body.remove();
                        // }
                    }
                })
                .catch(() => {
                    console.log(res.data);
                })
        });


        // comment ajax
        let submitComment = document.getElementById("comment-submit-id");
        let textareaComment = document.getElementById("comment-textarea-id");
        let commentsContainer = document.getElementById("comments-container-id");
        let commentDates = document.getElementsByClassName("comment-date");

        for (let item = 0; item < commentDates.length; item++) {
            commentDates[item].textContent = commentDates[item].textContent.split(",")[0]
        }

        submitComment.addEventListener("click", (e) => {
            e.preventDefault();
            var cmfd = new FormData();
            cmfd.append('text', textareaComment.value);
            cmfd.append("csrfmiddlewaretoken", "{{csrf_token}}");
            axios.post("", cmfd)
                .then((e) => {
                    let _html = commentsContainer.innerHTML;
                    commentsContainer.innerHTML = "";
                    commentsContainer.innerHTML += `
      <div class="comments animate__animated animate__fadeInDown">
        <div class="comment-profile">
            <img src="{{request.user.image.url}}" alt="">
        </div>
        <div class="comment-main">
            <div class="comment-text">
                <a class="user" href="{% url 'profile' request.user %}"><strong>{{request.user}}</strong></a>
                ${textareaComment.value}
            </div>
            <div class="comment-info">
                <div class="comment-date">0s</div>
                <div class="comment-likes">
                    <span class="like-counts">0</span> <span class="like-word">Like</span>
                </div>
                <div class="comment-reply">Reply</div>
            </div>
        </div>
        <div class="comment-like" data-id="${e.data.id}" data-action="like">
            <i class="far fa-heart"></i>
        </div>
      </div>
      `;
                    commentsContainer.innerHTML += _html;
                    textareaComment.value = "";
                    console.log(e.data.id)
                })
                .catch(() => {
                    console.log("error");
                })
        });

        // comment like ajax
        let btnHearts = document.getElementsByClassName("comment-like");
        for (let index in btnHearts) {
            btnHearts[index].addEventListener("click", () => {
                let id = btnHearts[index].getAttribute("data-id");
                let action = btnHearts[index].getAttribute("data-action");
                let heartIcon = btnHearts[index].getElementsByClassName("fa-heart")[0];
                let commentLikes = document.getElementsByClassName("comment-likes")[index];
                let likeNumbers = (commentLikes.getElementsByClassName("like-counts")[0]);
                let likeWord = commentLikes.getElementsByClassName("like-word")[0];

                var cmLikeFd = new FormData();
                cmLikeFd.append("id", id);
                cmLikeFd.append("action", action);
                cmLikeFd.append("csrfmiddlewaretoken", "{{csrf_token}}");
                axios.post("", cmLikeFd)
                    .then((e) => {
                        if (action == "like") {
                            heartIcon.classList.remove("far");
                            heartIcon.classList.add("fas");
                            heartIcon.classList.add("heart-active");
                            btnHearts[index].setAttribute("data-action", "dislike");
                            // commentLikes.textContent = "";
                            if (parseInt(likeNumbers.textContent) >= 1) {
                                likeNumbers.textContent = (parseInt(likeNumbers.textContent) + 1);
                                likeWord.textContent = "Likes"
                            } else {
                                likeNumbers.textContent = (parseInt(likeNumbers.textContent) + 1);
                                likeWord.textContent = "Like";
                            }

                        } else {
                            heartIcon.classList.remove("fas");
                            heartIcon.classList.remove("heart-active");
                            heartIcon.classList.add("far");
                            btnHearts[index].setAttribute("data-action", "like");

                            if (parseInt(likeNumbers.textContent) <= 2) {
                                likeNumbers.textContent = (parseInt(likeNumbers.textContent) - 1);
                                likeWord.textContent = "Like"
                            } else {
                                likeNumbers.textContent = (parseInt(likeNumbers.textContent) - 1);
                                likeWord.textContent = "Likes"
                            }
                        }

                        console.log(e.data.status)
                    })
                    .catch((e) => {
                        console.log(e.status)
                    })
            });
        }


    <!-- actions -->

    // actions show
    let heartKey = document.getElementsByClassName("heart")[0];
    let actionsContainer = document.getElementsByClassName("actions-container")[0];

    document.addEventListener("click", (e)=>{
        if (!e.target.classList.contains("fa-heart") && !e.target.classList.contains("actions-container") && actionsContainer.classList.contains("show-box")){
            actionsContainer.classList.remove("show-box");
        }
    });
    heartKey.addEventListener("click", ()=>{
        actionsContainer.classList.toggle("show-box");
    });



    // modal profile box
    let modalProfile = document.getElementsByClassName("profile-modal-container")[0];
    let profile = document.getElementsByClassName("profile")[0];

    profile.addEventListener("click", () => {
        modalProfile.classList.toggle("display-none");
    });
    document.addEventListener("click", e => {
        if (!e.target.classList.contains("profile-box")){
            modalProfile.classList.add("display-none");
        }
    })


