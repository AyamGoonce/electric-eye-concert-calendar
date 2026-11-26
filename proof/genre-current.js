(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a467d1f8c76e2313.js","sha256":"a467d1f8c76e231358dccf94e068be7bf987b0e2cf90e7bf4ae0ea2405ad2235","count":244});
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
