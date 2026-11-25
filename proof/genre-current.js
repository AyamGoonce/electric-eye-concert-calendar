(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6a86bfbc20e104e9.js","sha256":"6a86bfbc20e104e96a2f47ba7928a75d527d18cc8b3aa54f243ba6ecd7859f3f","count":244});
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
