(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bfcb3ea2fc71e298.js","sha256":"bfcb3ea2fc71e29806946e3ba02ec056645fb6de964831aeec2f934bbe8ea441","count":2158,"publishedAt":"2026-10-14T22:12:33Z","state":"calendar-state.json","stateSha256":"44e70acb5306414d54702938f1f761683b8686a9f3e8c0dbffd69e4461a2bd49","sourceState":"calendar-source-state.json","sourceStateSha256":"6a44482d4f8665be89a190c666c6b5227a8c817d125211e23395394146054232"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
