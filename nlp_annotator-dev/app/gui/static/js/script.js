// COLLAPSIBLE VIEW FUNCTION
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}


// FADE OUT ALERTS
var close = document.getElementsByClassName("btn-close");
var i;

for (i = 0; i < close.length; i++) {
  close[i].onclick = function(){
    var div = this.parentElement;
    div.style.opacity = "0";
    setTimeout(function(){ div.style.display = "none"; }, 600);
  }
}


// TABLESORTER
$(function() {
  $("table").tablesorter();
});


// CONDITIONAL FORM FOR PATIENT ANNOTATION
// $('#id_CognitiveConcern').show();

// var cognitive_concern = $('#id_CognitiveConcern option:selected').text();

// if (cognitive_concern == 'Cognitive Concern') {
  
//   $('.id_SyndromicDiagnosis').show();

//   var syndromic_dx = $('#id_SyndromicDiagnosis option:selected').text();

//   if (syndromic_dx == 'Cognitive Impairment Not Dementia') {
//     $('.id_CINDSeverity').show();
//     $('.id_DementiaSeverity').hide();  
//   } else if (syndromic_dx == 'Dementia') {
//     $('.id_DementiaSeverity').show();
//     $('.id_CINDSeverity').hide(); 
//   } else {
//     $('.id_DementiaSeverity').hide();
//     $('.id_CINDSeverity').hide(); 
//   }

// } else {
//   $('.id_SyndromicDiagnosis').hide();
//   $('.id_DementiaSeverity').hide();  
//   $('.id_CINDSeverity').hide(); 
// }

// $('#id_CognitiveConcern').change(function () {

//   var cognitive_concern = $('#id_CognitiveConcern option:selected').text();

//   if (cognitive_concern == 'Cognitive Concern') {
    
//     $('.id_SyndromicDiagnosis').show();

//     var syndromic_dx = $('#id_SyndromicDiagnosis option:selected').text();

//     if (syndromic_dx == 'Cognitive Impairment Not Dementia') {
//       $('.id_CINDSeverity').show();
//       $('.id_DementiaSeverity').hide();  
//     } else if (syndromic_dx == 'Dementia') {
//       $('.id_DementiaSeverity').show();
//       $('.id_CINDSeverity').hide(); 
//     } else {
//       $('.id_DementiaSeverity').hide();
//       $('.id_CINDSeverity').hide(); 
//     }

//   } else {
//     $('.id_SyndromicDiagnosis').hide();
//     $('.id_DementiaSeverity').hide();  
//     $('.id_CINDSeverity').hide(); 
//   }

// });

// $('#id_SyndromicDiagnosis').change(function () {

//   var syndromic_dx = $('#id_SyndromicDiagnosis option:selected').text();

//   if (syndromic_dx == 'Cognitive Impairment Not Dementia') {
//     $('.id_CINDSeverity').show();
//     $('.id_DementiaSeverity').hide();  
//   } else if (syndromic_dx == 'Dementia') {
//     $('.id_DementiaSeverity').show();
//     $('.id_CINDSeverity').hide(); 
//   } else {
//     $('.id_DementiaSeverity').hide();
//     $('.id_CINDSeverity').hide(); 
//   }

// });

// SCROLL TO CURRENT NOTE/KEYWORD
$(document).ready(function(){

  // TIMELINE

  var url = window.location.href;

  var splitBySlash = url.split("/");
  console.log(splitBySlash);
  
  var finalId = splitBySlash[4] + "-" + splitBySlash[5] + "-timeline";
  console.log(finalId);

  jQuery(".timeline").animate({  
    scrollTop: jQuery("#" + finalId).offset().top
  });


  // KEYWORDS

  // var keywords = document.getElementsByClassName('note-keyword');
  // var counter = 0;
  // console.log(keywords);

  // $("#next-keyword-button").click(function(){
    
  //   for (var x = 0; x < keywords.length; x++) {
  //     keywords[x].id = 'keyword-inactive';
  //   }

  //   if (counter > keywords.length){
  //     counter = 0;
  //   }

  //   keywords[counter].id = 'keyword-active';

  //   jQuery("#note-text").animate({  
  //     scrollTop: jQuery("#keyword-active").offset().top - 330
  //   });
  //   counter++;

  // });

});