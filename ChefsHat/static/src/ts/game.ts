document.addEventListener("DOMContentLoaded", () => {
    const SHARED_DATA = {
        is_pizza:               ((<any>window)._sharedData.IS_PIZZA              as string === 'True') ?? false,
        player_turn:            parseInt((<any>window)._sharedData.PLAYER_TURN),
        simulate_next_actions:  ((<any>window)._sharedData.SIMULATE_NEXT_ACTIONS as string  === 'True') ?? false,
        oponents_action:        ((<any>window)._sharedData.OPONENTS_ACTION       as string  === 'True') ?? false,
        has_error_message:      ((<any>window)._sharedData.HAS_ERROR_MESSAGE     as string  === 'True') ?? false,
        action_done:      ((<any>window)._sharedData.ACTION_DONE     as string  === 'True') ?? false,
    };
    const overlayElem: HTMLElement = document.getElementById("overlay");
    const playerContainer: HTMLElement = document.getElementById("playerAction");
    const allModals: HTMLCollection = document.getElementsByClassName("modal");
    const modalPlayer: HTMLElement = document.getElementById("modalPlayer");
    const cardsContainer: Element = modalPlayer.getElementsByClassName("container__player--cards")[0];
    const modalPlayerButton: Element = modalPlayer.getElementsByClassName("form__button")[0];
    const modalOpeningAnimationClass: string = "modal--opening";
    const modalClosingAnimationClass: string = "modal--closing";
    let xTouchDown: number | null = null;
    let yTouchDown: number | null = null;

    //=== Handle touch start
    function handleTouchStart(evt: any) {
        xTouchDown = evt.touches[0].clientX;
        yTouchDown = evt.touches[0].clientY;
    };          
    
    //=== Handle touch swipe
    function handleTouchMove(evt: any) {
        if (!xTouchDown || !yTouchDown)
            return;
        
        const xTouchUp = evt.touches[0].clientX; 
        const yTouchUp = evt.touches[0].clientY;
        
        let xDiff = xTouchDown - xTouchUp;
        let yDiff = yTouchDown - yTouchUp;

        if (Math.abs(xDiff) > Math.abs(yDiff)) {
            if (xDiff > 0) {
                /* left swipe */ 
            } else {
                /* right swipe */
            }
        } else {
            if (yDiff > 0) {
                /* up swipe */ 
            } else { 
                /* down swipe */
                handleModalClosing(modalPlayer);
            }                                                                 
        }
        
        xTouchDown = null;
        yTouchDown = null;                                             
    };

    function handleClick(evt: any) {
        const target = <HTMLElement>evt.target  

        for (let i = 0; i < allModals.length; i++) {
            if (!isTargetModal(target) && allModals[i].classList.contains(modalOpeningAnimationClass)) {
                handleModalClosing(allModals[i] as HTMLElement);
            }
        };
    }

    //=== Check if event came from modal
    function isTargetModal(target: HTMLElement): boolean {
        let isFromModal = false;
        let elems: HTMLElement[] = [];

        while (!isFromModal && target.classList.length > 0) {
            if (target.classList.contains('modal')) {
                isFromModal = true;
            }

            elems.unshift(target);
            target = target.parentNode as HTMLElement;
        }
        return isFromModal;
    }

    function handleModalOpening(modalElem: HTMLElement) : void {
        modalElem.classList.remove('hidden');

        if (overlayElem.classList.contains('hidden'))
            overlayElem.classList.remove('hidden')

        if (!modalElem.classList.contains(modalOpeningAnimationClass)) {
            modalElem.classList.remove(modalClosingAnimationClass)
            modalElem.classList.add(modalOpeningAnimationClass);
        }
    }

    function handleModalClosing(modalElem: HTMLElement): void {
        const animationDuration = window.getComputedStyle(document.documentElement).getPropertyValue('--animation-global-duration');
        const animationDurationSecond = parseFloat(animationDuration.replace(/\D+$/g, '')); //=== Remove s from duration

        if (modalElem.classList.contains(modalOpeningAnimationClass)) {
            modalElem.classList.add(modalClosingAnimationClass)
            modalElem.classList.remove(modalOpeningAnimationClass);
        }

        /* Hide after animation end */
        setTimeout(() => {
            if (!overlayElem.classList.contains('hidden'))
                overlayElem.classList.add('hidden')

            modalElem.classList.add('hidden');
        }, animationDurationSecond * 1000);
    }

    function handleFormWithDelay(form: HTMLFormElement, timing = 1000): void {
        setTimeout(() => { form.submit(); }, timing);
    };

    function isChecked(elem: HTMLElement): boolean {
        return (<HTMLInputElement>elem.getElementsByTagName('input')[0]).checked;
    }

    function handleCardsSelection(): void {
        const cardsArray = Array.from(modalPlayer.getElementsByClassName('card'));

        if (cardsArray.some(isChecked))
            modalPlayerButton.classList.remove('disabled');
        else
            modalPlayerButton.classList.add('disabled');
    }

    function handlePlayerModal(event: any): void {
        event.stopPropagation();
        
        if (SHARED_DATA.player_turn === 0)
            handleModalOpening(modalPlayer);
    }
    
    //=== Event binding
    window.addEventListener("click", handleClick);
    playerContainer.addEventListener("click", handlePlayerModal);
    cardsContainer.addEventListener("click", handleCardsSelection);
    modalPlayer.addEventListener('touchstart', handleTouchStart, false);
    modalPlayer.addEventListener('touchmove', handleTouchMove, false);


    //=== Handle action
    if (typeof SHARED_DATA !== 'undefined') {
    //=== Show last action

        if(SHARED_DATA.action_done){
            console.info('Show last action');
            const modalActionDone = <HTMLElement>allModals.namedItem('modalActionDone')
            setTimeout(() => {
                   handleModalOpening(modalActionDone);

        }, 1000);

             setTimeout(() => {
               handleModalClosing(modalActionDone);
        }, 2000);


        }


        switch(true) {

             //=== error
            case (SHARED_DATA.has_error_message):
                console.info('Invalid move');
                const modalError = <HTMLElement>allModals.namedItem('modalError')
                handleModalOpening(modalError);
                break;
            //=== Action simulation
            case (SHARED_DATA.oponents_action && SHARED_DATA.simulate_next_actions):
                console.info('Action simulation');
                const modalAction = <HTMLElement>allModals.namedItem("modalAction");
                const nextActionForm = <HTMLFormElement>document.getElementById("formNextAction");
                handleModalOpening(modalAction);
                handleFormWithDelay(nextActionForm);
                break;
            //=== Pizza ready
            case (SHARED_DATA.is_pizza):
                console.info('Pizza ready');
                const modalPizza = <HTMLElement>allModals.namedItem("modalPizza");
                const formPizza = <HTMLFormElement>document.getElementById("formPizza");
                handleModalOpening(modalPizza);
                handleFormWithDelay(formPizza, 3000);
                break;
            //=== Opponents turn
            case (SHARED_DATA.player_turn !== 0 && SHARED_DATA.oponents_action):
                console.info('Adversaries turn');
                const opponentForm = <HTMLFormElement>document.getElementById('opponentForm') as HTMLFormElement;
                handleFormWithDelay(opponentForm, 1500);
                break;
            //=== Player turn
            case (SHARED_DATA.player_turn === 0 && !SHARED_DATA.has_error_message):
                console.info('Player turn');
                handleModalOpening(modalPlayer);
                break;
        }
    }
});