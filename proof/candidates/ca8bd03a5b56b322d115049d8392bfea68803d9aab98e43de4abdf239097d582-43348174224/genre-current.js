(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e4952319b3a27c7a.js","sha256":"e4952319b3a27c7a9a59c82194d3bd2366c31b9a1f5f17b479919a4dfecb7f72","count":244});
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
