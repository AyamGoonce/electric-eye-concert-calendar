(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.78fd3eb70b51a67a.js","sha256":"78fd3eb70b51a67a66b14062943bfc642d8292691a0cdf2a220db921b40fd5bb","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
