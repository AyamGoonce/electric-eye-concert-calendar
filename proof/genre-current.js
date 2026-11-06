(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.54af94f4ee3e26f8.js","sha256":"54af94f4ee3e26f89da3c54976158a5d831edb9d19acbf9b82e94b82d680b720","count":244});
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
