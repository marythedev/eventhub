const paginationPagesBtns = document.querySelectorAll(".pagination-pages .pagination-page, .pagination-pages a.pagination-page");

let activeIndex;
paginationPagesBtns.forEach((el, index) => {
    if (el.classList.contains("active")) {
        activeIndex = index;
    }
});

// add .prev-page & .next-page to the corresponding page links next to active page
if (activeIndex != undefined) {
    if (paginationPagesBtns[activeIndex - 1])
        paginationPagesBtns[activeIndex - 1].classList.add("prev-page");

    if (paginationPagesBtns[activeIndex + 1])
        paginationPagesBtns[activeIndex + 1].classList.add("next-page");
}