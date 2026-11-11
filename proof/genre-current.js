(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.2a041b41641b0010.js","sha256":"2a041b41641b0010ab48bf36312dd91ed8f3ec148704d58a08160d65d1e7b8ec","count":244});
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
