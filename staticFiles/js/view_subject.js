// // static/js/category.js
// $(document).ready(function () {
//     console.log("AJAX Script loaded");

   
//     $('.view-subjects-btn').click(function () {
//     const btn = $(this);
//     const categoryId = btn.data('category-id');
//     const container = $('#subjects-' + categoryId);
//     const subjectList = container.find('ul');
//     const loader = $('#loader-' + categoryId);

//     if (container.hasClass('d-none')) {
//     container.removeClass('d-none');
//     loader.show();

//     // Only load once
//     if (subjectList.children().length === 0) {
//         $.ajax({
//         url: '/subject/by-category/' + categoryId + '/',
//         type: 'GET',
//         success: function (data) {
//             loader.hide();
//             if (data.subjects.length > 0) {
//             $.each(data.subjects, function (index, subject) {
//                 subjectList.append('<li class="list-group-item bg-light text-dark">' + subject.name + '</li>');
//             });
//             } else {
//             subjectList.append('<li class="list-group-item bg-light text-muted">No subjects found.</li>');
//             }
//         },
//         error: function () {
//             loader.hide();
//             subjectList.append('<li class="list-group-item bg-danger text-white">Error loading subjects.</li>');
//         }
//         });
//     }
//     } else {
//     container.addClass('d-none');
//     }
//     });

    
//     console.log("AJAX Script loaded");

    
// });







