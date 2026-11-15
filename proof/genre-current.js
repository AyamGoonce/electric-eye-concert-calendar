(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e9c405ea7c181f10.js","sha256":"e9c405ea7c181f109ab571662cdb9894d649f8daf96c69ee4d95d8ad2e933c77","count":244});
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
