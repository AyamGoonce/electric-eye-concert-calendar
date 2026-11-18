(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.964ffa049bcb8957.js","sha256":"964ffa049bcb8957d050a2b7cb4d34f21abe3cfaab5a72e764cb352a56fd3f0c","count":244});
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
