(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.972cba01bec0037b.js","sha256":"972cba01bec0037bf9ad8104a69ff6acc0ef70d208ab9e65a9a7325a84fad0a4","count":244});
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
