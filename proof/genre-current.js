(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3aa27dab5837b6d6.js","sha256":"3aa27dab5837b6d6dab6727452575e1cc113d06e9ddd59c8b53d12f28a37d7c6","count":244});
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
