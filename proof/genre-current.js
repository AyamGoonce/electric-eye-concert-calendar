(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.db719fb24333d28b.js","sha256":"db719fb24333d28b9f11dc9dc258e6c1850ae319b6052af40a8ef8b316a92ca5","count":244});
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
