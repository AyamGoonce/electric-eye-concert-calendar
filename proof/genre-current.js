(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.67dd0ca0d56fa8ce.js","sha256":"67dd0ca0d56fa8cef895c506464a4e7f15bf7b197972512a08e8092b75153eaf","count":208});
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
