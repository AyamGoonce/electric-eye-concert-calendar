(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8a153ea9efb4e02a.js","sha256":"8a153ea9efb4e02ab48faf38d7d58bfd2029aee24cf6cca0f7495ac069f44537","count":244});
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
