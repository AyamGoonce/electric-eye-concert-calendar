(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.36df433a48a36a01.js","sha256":"36df433a48a36a015cebb0c2ac290df0f79da18c13f83832b31a7d4106f0afe6","count":244});
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
