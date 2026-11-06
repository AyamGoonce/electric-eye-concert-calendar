(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.91f8c3478ae332c9.js","sha256":"91f8c3478ae332c9b68c66afe6b656bd4f78349da087d7eac0ea47fa9f19dd46","count":244});
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
