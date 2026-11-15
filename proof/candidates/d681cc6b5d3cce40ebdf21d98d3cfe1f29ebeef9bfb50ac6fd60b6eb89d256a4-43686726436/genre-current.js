(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7abde3d2d80812f2.js","sha256":"7abde3d2d80812f2d375fbe93f879de3f12085bc8fc686f209770db6fe88ef39","count":244});
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
