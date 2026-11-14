(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f3608b469def456f.js","sha256":"f3608b469def456fc17ac276bd20eee82a49ec6f45aecf96172bf5d193bfbdd7","count":244});
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
