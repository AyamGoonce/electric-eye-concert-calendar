(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d8216924c6d15d79.js","sha256":"d8216924c6d15d795b10bebd418458952ace3118f2e048b939e5563ad4b4d7fa","count":244});
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
