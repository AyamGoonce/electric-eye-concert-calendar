(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f5899c0d38f8a68c.js","sha256":"f5899c0d38f8a68cf2f7d366060ce7d72382058463d54dcff17de4b5401957db","count":244});
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
